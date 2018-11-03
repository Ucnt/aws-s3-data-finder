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
        record.levelname = record.levelname.replace(
                                                    "CRITICAL",colored("*","red", attrs=['bold'])
                                                   ).replace(
                                                    "ERROR",colored("*","yellow", attrs=['bold'])
                                                   ).replace(
                                                    "WARNING",colored("*","green", attrs=['bold'])
                                                   )
        return logging.Formatter.format(self, record)

formatter_stdout = MyFormatter('''{level} {message}'''.format(
    level='[%(levelname)s]', 
    message='%(message)s'
))

#Short format for printing to screen with newline option (e.g. if doing a progressbar)
# formatter_stdout = MyFormatter('''{new_line}{level} {message}'''.format(
#     new_line='%(new_line)s',
#     level='[%(levelname)s]', 
#     message='%(message)s'
# ))

#Verbose format for logging to file
formatter_file = logging.Formatter('''{asctime} | {level} | {message}'''.format(asctime='%(asctime)s',level='%(levelname)s',message='%(message)s'))


class Logger():
    def __init__(self, print_verbose, print_very_verbose):
        self.log = logging.getLogger()

        #Add rotating file handler
        fh = RotatingFileHandler("%s/log.txt" % (log_dir), maxBytes=200000, backupCount=5)
        fh.setLevel(logging.WARNING)
        fh.setFormatter(formatter_file)
        self.log.addHandler(fh)

        #Add command line handliner
        ch = logging.StreamHandler()
        if print_very_verbose:
            ch.setLevel(logging.WARNING)
        elif print_verbose:
            ch.setLevel(logging.ERROR)
        else:
            ch.setLevel(logging.CRITICAL)
        ch.setFormatter(formatter_stdout)
        self.log.addHandler(ch)


#Create the logger
logger = Logger(print_verbose=args.print_verbose, print_very_verbose=args.print_very_verbose)
