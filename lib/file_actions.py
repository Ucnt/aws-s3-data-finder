#!/usr/bin/env python3
'''
Purpose: Variety of file action base methods, e.g. 
    - Adding a file
    - Getting array from splitlines
    - Searching for a string in one of the linessearching for

Author: Matt vensson (UCnt)
'''
from lib.logger import *
from lib.traceback import *


def string_in_line(file_name, string_search, exact_match=True):
    """Returns True if the string was found in a line in the file, False if not"""
    try:
        with open(file_name, "r") as f:
            for line in f:
                if string_search in line.strip():
                    return True
        return False
    except:
        logger.log.critical("Error searching for %s in %s: %s" % (string_search, file_name, get_exception().replace("\n", " ")))


def add_string_to_file(file_name, string_to_add):
    """Adds the given string to the given file name"""
    try:
        with open(file_name, "a") as f:
            f.write("%s\n" % (string_to_add))
    except:
        logger.log.critical("Error adding %s to %s: %s" % (string_to_add, file_name, get_exception().replace("\n", " ")))


def list_from_lines(file_name, to_lower=False):
    """Returns an array of items, where each item is a line in the file"""
    try:
        items = []
        with open(file_name, "r") as f:
            #Be sure you're not adding any empty lines...might mess something up if you're checking the array.
            for line in f:
                if line.strip():
                    if to_lower:
                        items.append(line.strip().lower())
                    else:
                        items.append(line.strip())
        return items
    except:
        logger.log.critical("Error getting list from %s - %s" % (file_name, get_exception().replace("\n", " ")))
        return []