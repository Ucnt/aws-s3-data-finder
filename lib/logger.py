#!/usr/bin/env python3
from lib.constants import *
from lib.arg_parser import *
import logging
from logging.handlers import RotatingFileHandler
import os
from termcolor import colored


class MyFormatter(logging.Formatter):
    """
        Custom Formatter with colored [*], based on criticality, instead of words
        You could theoretically change * to anything, e.g. VULN, ERROR, INFO...even just colored CRITICAL, ERROR, WARNING
    """
    def format(self, record):
        #Make the custom level marker
        record.levelname = record.levelname.replace(
                                                    "CRITICAL",colored("*","red", attrs=['bold'])
                                                   ).replace(
                                                    "ERROR",colored("*","yellow", attrs=['bold'])
                                                   ).replace(
                                                    "WARNING",colored("*","green", attrs=['bold'])
                                                   )
        
        #Make the newline start before the level if there is one in the message
        if record.message.startswith("\n"):
            record.level_label = "\n[%s]" % (record.levelname)
        else:
            record.level_label = "[%s]" % (record.levelname)

        #Be sure message is stripped either way
        record.message_text = record.message.strip()

        #Return the newly formatted record
        return logging.Formatter.format(self, record)


class Logger():
    def __init__(self, print_verbose, print_very_verbose):
        self.log = logging.getLogger()

        #Add rotating file handler
        fh = RotatingFileHandler("%s/log.txt" % (log_dir), maxBytes=200000, backupCount=5)
        fh.setLevel(logging.WARNING)
        formatter_log = logging.Formatter('''{asctime} | {level} | {message}'''.format(asctime='%(asctime)s',level='%(levelname)s',message='%(message)s'))
        fh.setFormatter(formatter_log)
        self.log.addHandler(fh)

        #Add command line handliner
        ch = logging.StreamHandler()
        #Set the level
        if print_very_verbose:
            ch.setLevel(logging.WARNING)
        elif print_verbose:
            ch.setLevel(logging.ERROR)
        else:
            ch.setLevel(logging.CRITICAL)
        #Custom format for printing to the screen
        formatter_stdout = MyFormatter('''{level_label} {message_text}'''.format(
            level_label='%(level_label)s', 
            message_text='%(message_text)s'.strip()
        ))
        ch.setFormatter(formatter_stdout)
        self.log.addHandler(ch)


#Create the logger
logger = Logger(print_verbose=args.print_verbose, print_very_verbose=args.print_very_verbose)
