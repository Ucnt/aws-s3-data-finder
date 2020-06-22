#!/usr/bin/env python3
#
# Forked from Romuald Brunet, https://stackoverflow.com/questions/3160699/python-progress-bar
#
import os
import sys
import re
import math
import time, datetime


class ProgressBar(object):
    def __init__(self, num_items):
        """Initialized the ProgressBar object"""
        #Output format and variables
        self.symbol = "#"               #Needs to be 1 char
        self.fmt = '''%(percent)3d%% %(progress_bar)s %(cur_item)s of %(num_items)s   %(items_per_time)s%(per_time_label)s    Skipped: %(num_skipped)s   Run Time: %(run_time)s   Item: %(item)s%(end_spaces)s'''
        assert len(self.symbol) == 1    #If higher, progress bar won't populate properly
        try:
            self.progressbar_width = math.floor(int(os.popen('stty size', 'r').read().split()[1])*.35)
        except:
            self.progressbar_width = 40                 #Length of progress bar
        
        # Add end spaes to stop ghost characters.  Keep in the call in case screen size changes
        self.end_spaces = " " * 5

        #Vars related to counts/time
        self.start_epoch = int(time.time())         #Assumes you create the object just as you start the first item
        self.finished = False
        self.num_items = num_items
        self.cur_item = 0
        self.num_skipped = 0


    def __call__(self, num_completed=1, item=""):
        """Actions to run when progress is run"""

        #Update calculations/values
        self.cur_item += num_completed

        #Calculate the percent or set to 0 if no total items, e.g. creating a bar to process from 0
        try:
            percent = self.cur_item / float(self.num_items)
        except ZeroDivisionError:
            percent = 0

        #Make the progress bar
        bar_fill_size = int(self.progressbar_width * percent)
        progress_bar = "%s%s" % ((self.symbol * bar_fill_size) , (' ' * (self.progressbar_width - bar_fill_size)))

        run_time = time.time() - self.start_epoch

        items_remaining = self.num_items - self.cur_item

        #Check to be sure that your cur_item item is not 0
        try:
            time_left = (run_time/self.cur_item) * items_remaining
        except ZeroDivisionError:
            time_left = 0

        #Calculate how many items per second or minute or hr are being processed, adding appropriate label
        items_per_time = int(self.cur_item / run_time)
        per_time_label = "/sec"
        if items_per_time == 0:
            items_per_time = int(self.cur_item / run_time * 60)
            per_time_label = "/min"
            if items_per_time == 0:
                items_per_time = int(self.cur_item / run_time * 60 * 60)
                per_time_label = "/hr"

        #Args to populate into fmt
        args = {
            'percent': (percent * 100),
            'progress_bar': '''[{progress_bar}]'''.format(progress_bar=progress_bar),
            'cur_item': "{:,}".format(self.cur_item),
            'num_items': "{:,}".format(self.num_items),
            'num_skipped': "{:,}".format(self.num_skipped),
            'items_per_time': items_per_time,
            'per_time_label': per_time_label,
            'run_time': self.get_eta(run_time, get_ms=True),
            'item': item,
            'end_spaces' : self.end_spaces,
        }

        #Print the update
        print(self.fmt%args, end="\r", flush=True)



    def get_eta(self, time_left, get_ms=False):
        """Return the time left/run in terms of months, days, hrs, min, and sec"""
        if not time_left:
            return "0s"
        else:
            time_items_remaining = time.gmtime(time_left)
            
            time_left_string = ""
            for item, value in (
                                ("mo", time_items_remaining.tm_mon-1),
                                ("d", time_items_remaining.tm_mday-1), 
                                ("h", time_items_remaining.tm_hour), 
                                ("m", time_items_remaining.tm_min), 
                                ("s", "%s.%s" % (time_items_remaining.tm_sec, str(time_left).split(".")[1][:7])),
                               ):
                if value:
                    if get_ms or item != "s":
                        time_left_string += "{value}{item} ".format(value=value, item=item)
                    else:
                        time_left_string += "{value}{item} ".format(value=value.split(".")[0], item=item)

            if time_left_string:
                return time_left_string
            else:
                return "0s"


    def done(self, print_final_output=True):
        """Marks the task as complete"""
        #Be sure done hasn't already been called, set if not
        if not self.finished:
            self.finished = True
            print("", flush=True)

