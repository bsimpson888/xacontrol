#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import logging.handlers
import os
import sys
from XAControl.XAControlServerApp import XAControlServerApp
from XAControl.WSGIServer import WSGIServer

__author__ = 'Marco Bartel'


class xacontrol(object):
    def __init__(self):
        XAControlServerApp.debug = False

        if sys.platform in ("posix", "linux2"):
            logDirectory = "/var/log"
        else:
            logDirectory = "c:\\temp"

        if not os.path.exists(logDirectory):
            os.makedirs(logDirectory)

        LOG_FILENAME = os.path.join(logDirectory, "xacontrol.log")
        LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

        # Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
        # Give the logger a unique name (good practice)
        logger = logging.getLogger(__name__)
        # Set the log level to LOG_LEVEL
        logger.setLevel(LOG_LEVEL)
        # Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
        handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
        # Format each log message like this
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        # Attach the formatter to the handler
        handler.setFormatter(formatter)
        # Attach the handler to the logger
        logger.addHandler(handler)


        # Make a class we can use to capture stdout and sterr in the log
        class MyLogger(object):
            def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

            def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                    self.logger.log(self.level, message.rstrip())

        if not XAControlServerApp.debug:
            # Replace stdout with logging to file at INFO level
            sys.stdout = MyLogger(logger, logging.INFO)
            # Replace stderr with logging to file at ERROR level
            sys.stderr = MyLogger(logger, logging.ERROR)

        self.app = XAControlServerApp()
        self.wsgi = WSGIServer(self.app, 808, logScreen=XAControlServerApp.debug)
        print "starting xacontrol..."
        self.wsgi.start()
        print "joining..."
        self.wsgi.join()
        print "This is the end....."


if __name__ == '__main__':
    xac = xacontrol()
