import logging
import logging.handlers
from logging import Formatter
import socket
import time
import sys
import config
from easyos import easyos

logging.Formatter.converter = time.gmtime
hostname = socket.gethostname()

class ContextFilter(logging.Filter):
    """Inject contextual information into the log."""

    def filter(self, record):
        record.HOSTNAME = hostname
        return True

syslog_ctf = ContextFilter()

# formatters:
# https://docs.python.org/3/library/logging.html#logrecord-attributes

class Logger:

    def __init__(self, formatter=None, log_level=config.DEFAULT_LOG_LEVEL, syslog_address="/dev/log"):

        if config.DEBUG and not formatter:
            self.formatter = Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
        elif not formatter:
            self.formatter = Formatter("%(asctime)s - %(levelname)s - %(message)s")
        else:
            self.formatter = formatter

        if not isinstance(getattr(logging, log_level.upper(), None), int):
            raise ValueError("Invalid log level: %s" % log_level)

        self.logger = logging.getLogger("yams")
        self.logger.setLevel(log_level)

        # stdout Console Handler
        self.ch = logging.StreamHandler(sys.stdout)
        self.ch.setLevel(log_level)
        self.ch.setFormatter(self.formatter)

        # https://docs.python.org/3/howto/logging.html#useful-handlers
        self.syslogger = logging.getLogger("syslog")
        self.syslogger.setLevel(log_level)

        try:
            self.syslog_handler = logging.handlers.SysLogHandler(address=syslog_address)
            self.syslog_handler.setFormatter(Formatter("%(asctime)s - host:%(HOSTNAME)s - %(name)s - %(levelname)s - %(message)s"))
            self.syslog_handler.addFilter(syslog_ctf)

            self.syslogger.addHandler(self.syslog_handler)
            self.logger.addHandler(self.syslog_handler)

        except FileNotFoundError as e:
            print("LOGGER :: Logging to syslog via '%s' failed: %s" % (
                str(syslog_address), str(e))
            )

        # if we're in debug mode, allow printing to stdout
        if config.DEBUG:
            self.logger.addHandler(self.ch)

    @property
    def syslog(self):
        return self.syslogger


if easyos["os"] == "Darwin":
    l = Logger(syslog_address="/var/run/syslog")
else:
    # or if network: syslog_address=("localhost", 514)
    l = Logger()

syslog = l.syslog # in case we want to send something only to syslog
log = l.logger


if __name__ == "__main__":
    #syslog.debug("Testing syslog.")
    log.debug("Testing logger.")
