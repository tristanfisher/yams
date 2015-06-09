import logging
import logging.handlers
import socket
import time
import sys

import config

logging.Formatter.converter = time.gmtime
hostname = socket.gethostname

# I think adding a ContextFilter obj to every request is wasteful overhead
# class ContextFilter(logging.Filter):
#     """Inject contextual information into the log."""
#     hostname = hostname
#
#     def filter(self, record):
#         record.hostname = ContextFilter.hostname
#         return True
# ctf = ContextFilter()
# syslogger.addFilter(ctf)


LOG_LEVEL = getattr(logging, 'DEBUG' if config.DEBUG else 'INFO')

class Logger(object):

    def __init__(self, log_level=LOG_LEVEL):

        self.syslogger = logging.getLogger('syslog')
        self.syslogger.setLevel(log_level)

        self.default_handler = logging.StreamHandler(sys.stdout)
        self.default_handler.setLevel(log_level)

        if config.DEBUG:
            formatter = logging.Formatter('%(filename)s - %(levelname)s - %(message)s')
        else:
            formatter = logging.Formatter('%(levelname)s - %(message)s')
        self.default_handler.setFormatter(formatter)

        try:
            self.syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
            self.syslog_handler.formatter = logging.Formatter('%(asctime)s %(hostname)s APP: %(message)s',
                                                              datefmt='%b %d %H:%M:%S')
            self.syslogger.addHandler(self.syslog_handler)
        except FileNotFoundError as e:
            print("LOGGER:: " + str(e))

    @property
    def logger(self):
        return self.syslogger


log = Logger()
logfile = log.logger


if __name__ == '__main__':
    logfile.info('test')