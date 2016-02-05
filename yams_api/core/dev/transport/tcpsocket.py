import select
import socket
import socketserver
import sys
import _thread
import time
from config import API
from yams_api.utils.logger import log

# ssl provides security, provide md5 as a cheap checksum
from hashlib import md5

from ctypes import Structure

# TODO: 31-Oct Client that quits on remote-end doesn't get removed from rlist -- gets stuck in CLOSE_WAIT


"""
shared secret / encryption details



    1 - compress
        - compress payload with zlib
            - this step is mostly to put it out of reach of trivial MITM/script kiddies when not using encryption,
            but carries other benefits as well

    2 - encrypt

        * initial key has to be cloak/dagger -- or could be pushed by config management or through an SSH tunnel

        - encrypt with key


how to encrypt/add non-repudiation?

see which is smaller, zlib->SSL or SSL->zlib

The tcpsockets for client/server come up with fixed attributes -- use slots instead of a dictionary for attributes

"""

# Python's socketserver handle conns synchronously.  Mix-in threading if using an object in your approach.
# Use these base classes in this order (due to overriding attrs) -- e.g. class TCPHandler(ThreadingMixIn, TCPServer).
# Resist the urge to simplify by using a StreamRequestHandler because we don't receive file-like objects w/ newlines


# ----------------------------------------------------------------------------------------------- #
# Socket wrapper / helper functions

def bytes_encoder(msg, encoding="utf-8"):
    return bytes(msg, encoding)


def md5_hash(msg, encoding="utf-8"):
    return md5(msg.encode(encoding)).hexdigest()


def client_thread(conn):
    msg = bytes_encoder("YAMS::\n")
    conn.send(msg)
    while True:
        # receive data from client
        data = conn.recv(1024)
        reply = bytes_encoder("Received: %s" % data)

        if not data:
            break

        conn.sendall(reply)
    conn.close()


def broadcast_message(server_socket, sock, conn_list, message):

    for client in conn_list:
        # don't broadcast to self and the server
        if client != server_socket and client != sock:
            try:
                client.send(message)

            # todo: be smarter here https://docs.python.org/3/library/socket.html#exceptions
            except:
                log.warn("Client (%s, %s) is not connected." % client)
                client.close()
                conn_list.remove(client)



# async send or receive and on completion of sending a batch add size of rx/tx to queue?
# queue should mutex on a rx/tx counter

#  Be aware of the following realities
#  - Send might not dump its buffers in a single pass
#  - Receive might not get > 1 char of a new message at a time
#  - The network is evil and sockets can hang for any reason.  Let the horror unfold in a thread without killing it.
#

#
# receive loop could be
#   def receive_msg_length()
#   def receive

#
# ntohl, htonl, ntohs, htons
# Network; Host; Shot; Long
#
#


def send(_sock, msg):
    # mutex or push to an array for processing when without the GIL
    #PROCESS_TX_BYTES += size of payload

    this_bytes_txd = 0

    # todo: get the real size of the message
    msg_len = len(msg)

    while this_bytes_txd < msg_len:
        tx_bytes = _sock.send(msg[this_bytes_txd:])
        if tx_bytes == 0:
            raise RuntimeError("Socket %s dropped" % _sock)
        this_bytes_txd = this_bytes_txd + tx_bytes


def receive(_sock, msg):
    # mutex or push to an array for processing when without the GIL
    #PROCESS_RX_BYTES += size of payload

    byte_chunks = []
    this_bytes_rxd = 0

    msg_len = 0


    while this_bytes_rxd < msg_len:

        current_chunk = _sock.recv(min(msg_len - this_bytes_rxd, API.SOCKET_RX_BUFFER_BYTES))

        if current_chunk == b'':
            raise RuntimeError("Socket %s dropped" % _sock)

        byte_chunks.append(current_chunk)
        this_bytes_rxd = this_bytes_rxd + len(current_chunk)

    return b''.join(byte_chunks)



# ----------------------------------------------------------------------------------------------- #

SOCKET_CONNECTIONS = []


# general metrics so we can expose how we're driving.
PROCESS_RX_BYTES = 0
PROCESS_TX_BYTES = 0


def make_server_socket():

    try:
        # Set up our socket and append it to our list of sockets we will be reading from

        # udp ip v4
        #sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # tcp ip v4
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # reuse local address, 6 == tcp from /etc/protocols. see man 3 getprotoent
        sock_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 6)

        sock_tcp.bind((API.LISTEN_HOST, API.LISTEN_PORT_SOCKET))

        # tolerate up to 10 unaccepted conns
        sock_tcp.listen(10)

        # don't block
        sock_tcp.setblocking(0)

        # it's okay if this becomes an expensive lookup, it only happens on first conn or to avoid crashing
        if not (sock_tcp in SOCKET_CONNECTIONS):
            SOCKET_CONNECTIONS.append(sock_tcp)

        return sock_tcp

    except (socket.error, Exception) as e:

        # catch any exception because we really just need to know why we failed
        log.fatal("Failed to create socket: %s" % e)
        sys.exit()


# ----------------------------------------------------------------------------------------------- #
def serve(POISON_PILL):

    sock_tcp = None

    rx_sockets = []
    tx_sockets = []
    err_sockets = []

    while True:

        # build a connection if we don't have one.  check none specifically.  don't make this a complex with
        # POISON_PILL -- it's possible we may need to have a listener for clients to drain their buffers
        if sock_tcp is None:
            sock_tcp = make_server_socket()

        try:
            # rlist - sockets to try reading; return from select is subset of actually readable (has data in buffer)
            # wlist - sockets to try writing to; return from select is subset of actually writable (outbound buffer available)
            # xlist - sockets to check for errors; return from select is subset of actually errored
            # select is blocking, so give it a timeout
            # "server" goes to rlist

            # socket to .connect() to clients gets appended into the wlist

            # see man select for more details
            try:
                rx_sockets, tx_sockets, err_sockets = select.select(SOCKET_CONNECTIONS, [], [], API.SOCKET_TIMEOUT_SECONDS)
            except KeyboardInterrupt:
                POISON_PILL = True

        except select.error as e:
            log.fatal("Could not select() on sockets.  Closing socket. %s " % e)
            # break here will jump to the close
            break

        # Please double-check the logic here
        # check for poison pill. bool is very slightly faster than constant int 1 comparison in py3.5
        if POISON_PILL:

            log.info("Received poison pill for shutdown.")
            # if we didn't have any clients between startup and shutdown, rx_sockets will be empty.
            if rx_sockets:
                for sock in rx_sockets:
                    try:
                        sock.shutdown(1)
                        # give it a little time for the socket to process the shutdown
                        time.sleep(.2)
                        sock.close()
                    except OSError:
                        # socket probably wasn't connected at .shutdown()
                        pass

                    SOCKET_CONNECTIONS.remove(sock)

            raise SystemExit('YAMS Socket Server exiting due to a poison pill.')



        # to respond to conversation initiated by a client (recv())
        for sock in rx_sockets:

            if sock == sock_tcp:
                # The server socket is responsible for accepting incoming connections and responding with its own client
                # connection socket.  We know we have a new client conn when data comes into our server socket buffer.

                # There shouldn't be an issue with this strategy for select/async with non-blocking sockets, but if so, this
                # would be where to dispatch a new thread/native thread
                socket_fd, address = sock_tcp.accept()
                SOCKET_CONNECTIONS.append(socket_fd)
                log.info("Client (%s, %s) connected" % address)
            else:
                # rx'd from a client

                try:
                    # message from the client here
                    rx_data = sock.recv(API.SOCKET_RX_BUFFER_BYTES)

                    # no exception, we have an rx_data
                    if rx_data:

                        # todo: process the data.  if way too large, disconnect client -- something is wrong..

                        # socket.send returns the number of bytes sent, so this should go to the metrics gather-er
                        # sendall returns None on success.  there is no way to determine how much data was sent on err, count bytes for tx size

                        # check for quit messages, evaluate based on the different yams event types

                        # socket.send returns the number of bytes sent, so this should go to the metrics gather-er
                        # sendall returns None on success.  there is no way to determine how much data was sent on err, count bytes for tx size

                        if not API.DEBUG:

                            # 1) Include zlib library and metadata about the request (+= zlib.ZLIB_VERSION)
                            # e.g. metadata: zlib=1.2.5
                            # 2) Checksum and store in checksum field (md5 or fletchers? fast, cheap - SSL does the security)
                            # 3) Compress (zlib.compress())
                            # 4) Encrypt

                            # with this order, if there's a corruption over the wire, zlib will see it as corrupted data
                            # then we'll have the checksum to compare the uncompressed payload against.

                            pass

                        # Else: Checksum, store checksum in message

                        sock.send(bytes_encoder("RECEIVED DATA: %s" % rx_data))


                # Probably errored on rx_data -- did something else deplete our buffer?
                # this next exception type is an educated guess -- couldn't get timing down for broken socket (e.g. ^c)
                except select.error as e:


                    # Probably fine that the connection is no longer there after initial connection.
                    # see man 2 accept
                    log.debug(str(e))
                    log.warn("Client socket <%s> is not connected." % sock)
                    # this could be harmless, but could be a sign of unintended clamping of client conns

                    # just close the conn and then remove it from our candidate FDs. don't bother with .shutdown(), but
                    # do close explicitly instead of assuming it will get GC'd
                    sock.close()
                    try:
                        log.info("Removing a socket due to a select error.")
                        SOCKET_CONNECTIONS.remove(sock)

                    except ValueError:
                        # sock wasn't in socket_connections. that's what we want, so that's fine.
                        continue



        # to initiate a conversation with a client (connect())
        for socket in tx_sockets:
            pass

        for socket in err_sockets:
            pass


        if API.DEBUG:
            log.debug("rlist: %s" % rx_sockets)
            log.debug("wlist: %s" % tx_sockets)
            log.debug("xlist: %s" % err_sockets)

        time.sleep(API.SOCKET_THREAD_YIELD_EPSILON)
        # poll for server shutdown on some interval too.  if we reach shutdown, tear down connections from clients

    # no longer True, exception raised, or we exited
    sock_tcp.close()