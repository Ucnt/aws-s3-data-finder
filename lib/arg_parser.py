#!/usr/bin/env python3
###############################################
## Purpose: Provies argument parsing capability
###############################################
import argparse

parser = argparse.ArgumentParser(description='''''')

###############################################
## Unauth Scan
###############################################
parser.add_argument('-u', '--unauthenticated', action='store_true', help='Run the search unauthenticated, via web request')
parser.add_argument('-e', '--endpoint', default="s3.amazonaws.com", help='Endpoint to use if doing an unauth scan.  Auth scan will use region in awscli')

###############################################
## Number of keys to pull
###############################################
parser.add_argument('-nk', '--num_keys', default=200000, help='Number of keys to get per bucket')

###############################################
## Bucket names or lists
###############################################
#Given bucket name or list of names
parser.add_argument('-n', '--bucket_name', default="", help='Name to run')
parser.add_argument('-nl', '--name_list', default="", help='List of names to run')

###############################################
## String options
###############################################
parser.add_argument('-c', '--characters', default="", help='Characters to run via random/bruteforce, e.g. "abcdefg.."')
parser.add_argument('-nc', '--num_chars', type=int, help='Lenght of bucket name"')
# parser.add_argument('-nr', '--num_range_characters', default="", help='Range lenght of bucket names, e.g. 3-5"')
parser.add_argument('-rc', '--random_chars', action='store_true', help='Run random chars"')
parser.add_argument('-ac', '--all_chars', action='store_true', help='Run all chars')
parser.add_argument('-pp', '--prefix_postfix', default='', help='Run with prefixes and/or postfixes - options: prefix, postfix, both')
parser.add_argument('-sa', '--start_after', default='', help='For all_chars, start after this string')

###############################################
## Optional
###############################################
#Rerun previously run buckets
parser.add_argument('--rerun', action='store_true', help="Rerun previously searched buckets")
#Rerun previously run buckets
parser.add_argument('--realert', action='store_true', help="Realert previously alerted suspicious files")
#Test mode just to see the bucket names
parser.add_argument('-t', '--test', action='store_true', help="Test mode to just print the bucket names being run")
#Print Bucket names as you go
parser.add_argument('-p', '--print_names', action='store_true', help="Print buket names as you go")
parser.add_argument('--no_follow_redirect', action='store_true', help="Don't follow redirects")

###############################################
## Debug Options
###############################################
parser.add_argument('-v', '--print_verbose', action='store_true', help="Print verbose (critical and errors)")
parser.add_argument('-vv', '--print_very_verbose', action='store_true', help="Print very verbose (critical, errors, and warnings")

#Compile the argument paser options
args = parser.parse_args()
