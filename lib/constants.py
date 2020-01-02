#!/usr/bin/env python3
import os
from lib.file_actions import list_from_lines

#Current file directory
lib_dir = os.path.dirname(os.path.realpath(__file__))
main_dir = os.path.dirname(os.path.dirname(__file__))
log_dir = "%s/log" % (main_dir)
list_dir = "%s/list" % (main_dir)
bucket_dir = "%s/bucket" % (main_dir)


#Get list of buckets completed and create a generator to randomly look at new ones
buckets_checked = list_from_lines("%s/buckets-checked.txt" % (list_dir), to_lower=True)
suspicious_files_found = list_from_lines("%s/suspicious-files.txt" % (list_dir), to_lower=True)
