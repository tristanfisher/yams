import os
from yams_api import api
from yams_api import tcpsocket
from config import API
import multiprocessing as _mp
import signal
import time
from yams_api.utils.logger import log


api.config.from_object(os.environ.get("FLASK_API_CONFIG") or "config")
api.jinja_env.trim_blocks = True
api.jinja_env.lstrip_blocks = True

# Multi-process must be used because Flask uses signal, which can only work when it's the main thread.
# Since we'll need to do processes anyway, we'll make the best of it and add some graceful handlers
API_PROCESS_LIST = []

def api_http(ipc_queue=None):
    api.run(host=API.LISTEN_HOST, port=API.LISTEN_PORT, debug=API.DEBUG)


def api_socket(poison_pill, ipc_queue=None):
    tcpsocket.serve(poison_pill)


def soft_shutdown(signal_number, stack_frame):
    """
    Attempt to cleanly stop the running API processes.

    The socket and HTTP servers are continuously running processes, so we cannot simply join() on them and wait for
     them to finish.  Instead, clean up as we can and then terminate the procs.

     Note that a sigkill cannot be caught.

    Flask/HTTP close process:
        - stop pulling work off of the queue
        - let currently running methods finish.
        - terminate proc

    Socket shutdown process:
        - shutdown() to stop rx/tx, sending FIN/EOF.
        - close() to decrement a handle counter to the socket. if socket was shutdown, this should mean deallocation

        Shutdown options:
            0 - no more rx (SHUT_RD)
            1 - no more tx (SHUT_WR)
            2 - no more rx/tx (SHUT_RDWR)

        More verbosely:
        1) server "no more data will be sent" .shutdown(1)
        2) client receives and finishes sending its data to server, who is still listening for N duration
        3) client "no more data will be sent" .shutdown(1) -- could also optionally SHUT_RD or close at this point
        4) server receives #3 from all clients, can do a shutdown(2) if wanted or just close socket



    :param signal_number: signal integer from os signal
    :param stack_frame: stack frame at the top at the time of the signal
    :return:
    """
    log.info("Caught shutdown (code %s).  Attempting to gracefully close." % signal_number)

    def close_socket():

        log.debug("Setting poison pill to shut down the socket.")
        tcpsocket.POISON_PILL = True

        # for socket in rx_socket, wx_socket, err_sockets, shutdown
        # wait N duration
        # join


if __name__ == "__main__":

    log.info("Starting up.")
    if API.DEBUG:

        flask_reloader_sock_msg = "You will be receiving the error 'Failed to create socket: [Errno 48]...' " \
                                  "this is typical and due to Flask's reloader that gets called in debug mode."
        log.critical(flask_reloader_sock_msg)
        print(flask_reloader_sock_msg)

    # spawn a fresh process -- we don't have resources that we need to share via fork().
    # use a context in case our user wants to further subprocess.  check ipcs after failure mode testing
    # to make sure that this isn't problematic for named semaphores.
    _context = _mp.get_context('spawn')

    # create a general purpose internal queue -- useful for important messages like 'disconnect client x'.
    # unfortunately, POSIX semaphores require r/w to /dev/shm, which isn't there on OS X.
    # Leave here as a reminder that this functionality should be implemented.
    #ipc_queue = _context.Queue()
    # and pass as an arg to the Processes when ready.

    proc_api_http = _context.Process(target=api_http, name="API_HTTP")
    proc_api_socket = _context.Process(target=api_socket, name="API_SOCKET", args=(False,))

    API_PROCESS_LIST.append(proc_api_http)
    API_PROCESS_LIST.append(proc_api_socket)

    # handle interrupts/signals
    # http://www.gnu.org/software/libc/manual/html_node/Termination-Signals.html#Termination-Signals

    # ^c
    signal.signal(signal.SIGINT, soft_shutdown)

    # .terminate()
    signal.signal(signal.SIGTERM, soft_shutdown)

    proc_api_http.start()
    proc_api_socket.start()