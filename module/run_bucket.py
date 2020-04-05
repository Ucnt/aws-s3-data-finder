#!/usr/bin/env python3
import ast
import sys
import requests
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from lib.arg_parser import *
from lib.constants import *
from lib.logger import *
from lib.file_actions import *
from lib.get_cmd_output import *
from lib.traceback import *
min_db_mb = 500

def run_bucket(bucket_name):
    #If you're just testing, print the bucket name and return
    bucket_name = bucket_name.lower()
    if args.test:
        logger.log.critical("\n%s" % (bucket_name))
        return bucket_name
    elif args.unauthenticated:
        return run_bucket_unauth(bucket_name)
    else:
        return run_bucket_auth(bucket_name)
            

def run_bucket_unauth(bucket_name):
    '''
    Purpose: Run the bucket unauthenticated, i.e. via an HTTP request
    Reason: Might not want to leave any trace...e.g. with AWS keys
    '''
    global buckets_checked
    try:
        try:
            url = "https://{bucket_name}.{endpoint}".format(bucket_name=bucket_name, endpoint=args.endpoint)
            r = requests.get(url, timeout=5)
        except:
            url = "http://{bucket_name}.{endpoint}".format(bucket_name=bucket_name, endpoint=args.endpoint)
            r = requests.get(url, verify=False, timeout=5)
        add_string_to_file("%s/buckets-checked.txt" % (list_dir), string_to_add="%s.%s" % (bucket_name, args.endpoint))

        if "<Code>PermanentRedirect</Code>" in r.text:
            if args.no_follow_redirect:
                return bucket_name
            else:
                endpoint_redirect = re.findall("<Endpoint>(.+?)</Endpoint>", r.text)[0]
                try:
                    url = "https://{endpoint_redirect}".format(endpoint_redirect=endpoint_redirect)
                    r = requests.get(url, timeout=5)
                except:
                    url = "http://{endpoint_redirect}".format(endpoint_redirect=endpoint_redirect)
                    r = requests.get(url, verify=False, timeout=5)

        #See if the bucket doesn't exist
        for no_bucket_response in ["NoSuchBucket", "InvalidBucketName"]:
            if "<Code>{message}</Code>".format(message=no_bucket_response) in r.text:
                return bucket_name

        #See if bucket is disabled
        if "<Code>AllAccessDisabled</Code>" in r.text:
            add_string_to_file("%s/buckets-allaccessdisabled.txt" % (list_dir), string_to_add="%s.%s" % (bucket_name, args.endpoint))
            return bucket_name

        #See if access is denied
        if "<Code>AccessDenied</Code>" in r.text:
            add_string_to_file("%s/buckets-accessdenied.txt" % (list_dir), string_to_add="%s.%s" % (bucket_name, args.endpoint))
            return bucket_name

        #Bucket exists...add it
        add_string_to_file("%s/buckets-found.txt" % (list_dir), string_to_add="%s.%s" % (bucket_name, args.endpoint))

        #If it has no keys, stop
        if not "<Key>" in r.text:
            return bucket_name
        #Parse out the keys and look through them
        else:
            #Open XML
            key_dump = '''<?xml version="1.0" encoding="UTF-8"?><ListBucketResult>'''

            #Get all items
            num_keys = 0
            while True:
                #Stop at the max number of keys
                if num_keys >= args.num_keys:
                    break

                #Get all of the files
                files = re.findall("<Contents>(.+?)</Contents>", r.text)
                for file in files:
                    try:
                        key = re.findall("<Key>(.+?)</Key>", file)[0]
                        #Skip keys that are folder names
                        if key.endswith("/"):
                            continue
                        #Add the current key to the list
                        key_dump += "<Contents>%s</Contents>" % (file)
                        #Check the current key
                        check_key(bucket_name=bucket_name, key=key, file_size_mb=int(re.findall("<Size>(.+?)</Size>", file)[0])/1024/1024)
                        num_keys += 1
                    except:
                        logger.log.warning("\nError on %s: %s" % (bucket_name, get_exception().replace("\n","")))

                #Paginate, if necessary
                try:
                    if "<IsTruncated>true</IsTruncated>" in r.text:
                        next_rul = '''{url}?list-type=2&start-after={last_key}'''.format(url=url, last_key=re.findall("<Key>(.+?)</Key>", r.text)[-1])
                        r = requests.get(next_rul, verify=False)
                except:
                    logger.log.warning("\nError on %s: %s" % (bucket_name, get_exception().replace("\n","")))

            #Close XML and write it
            key_dump += '''</ListBucketResult>'''
            add_string_to_file(file_name="%s/%s.%s.xml" % (bucket_dir, bucket_name, args.endpoint), string_to_add=key_dump)
            buckets_checked.append("%s.%s" % (bucket_name.lower(), args.endpoint))
            add_string_to_file("%s/buckets-checked.txt" % (list_dir), string_to_add="%s.%s" % (bucket_name, args.endpoint))
        return bucket_name
    except:
        add_string_to_file("%s/buckets-errors.txt" % (list_dir), string_to_add="%s.%s" % (bucket_name, args.endpoint))
        logger.log.warning("\nError on %s: %s" % (bucket_name, get_exception().replace("\n","")))
        return bucket_name


def run_bucket_auth(bucket_name):
    global buckets_checked
    try:
        command = '''aws s3api list-objects --bucket %s --max-items %s''' % (bucket_name, args.num_keys)
        output = get_cmd_output(command)
        if "aws: not found" in output:
            logger.log.critical("AWS CLI not installed.  Install and configure it w/ access and secret keys before continuing: https://docs.aws.amazon.com/cli/latest/userguide/installing.html")
            sys.exit()
        elif "Unable to locate credentials" in output:
            logger.log.critical("AWS CLI credentials not configured.  Configure access and secret keys before continuing: https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html")
            sys.exit()
        elif not output.strip():
            pass
        elif "NoSuchBucket" in output:
            pass
        elif "Access Denied" in output:
            add_string_to_file("%s/buckets-accessdenied.txt" % (list_dir), string_to_add="%s.%s" % (bucket_name, args.endpoint))
            return bucket_name
        elif "AllAccessDisabled" in output:
            add_string_to_file("%s/buckets-allaccessdisabled.txt" % (list_dir), string_to_add="%s.%s" % (bucket_name, args.endpoint))
            return bucket_name
        else:
            add_string_to_file("%s/buckets-found.txt" % (list_dir), string_to_add="%s.%s" % (bucket_name, args.endpoint))
            output_json = ast.literal_eval(output.strip().replace('""', '"'))
            #Write the bucket content to file (in case you want to look back later)
            #if output_json['Contents']:
                #add_string_to_file(file_name="%s/%s.%s.json" % (bucket_dir, bucket_name, args.endpoint), string_to_add=output_json['Contents'])
            for item in output_json['Contents']:
                key = item['Key']
                #Skip keys that are folder names
                if key.endswith("/"):
                    continue
                check_key(bucket_name=bucket_name, key=key, file_size_mb=int(item['Size']/1024/1024))
        #Mark as done... 
        buckets_checked.append("%s.%s" % (bucket_name.lower(), args.endpoint))
        add_string_to_file("%s/buckets-checked.txt" % (list_dir), string_to_add="%s.%s" % (bucket_name, args.endpoint))
        return bucket_name
    except:
        add_string_to_file("%s/buckets-errors.txt" % (list_dir), string_to_add="%s.%s" % (bucket_name, args.endpoint))
        logger.log.warning("\nError on %s: %s" % (bucket_name, get_exception().replace("\n","")))
        return bucket_name


def check_key(bucket_name, key, file_size_mb):
    global suspicious_files_found
    try:
        key_lower = key.lower()
        msg = "{file_size_mb} -> {bucket_name}.{endpoint}/{key}".format(file_size_mb=file_size_mb, bucket_name=bucket_name, endpoint=args.endpoint, key=key)
        suspicious = False     # By default, not suspicous

        #Suspicious database/backup file
        if suspicious_backup(key_lower) and file_size_mb >= min_db_mb:
            suspicious = True
        #Potential docker releated files
        elif any([True for s in ["dockerfile", "docker-compose", "docker-container"] if s in key_lower]):
            suspicious = True
        #Potential credentials
        elif any([True for s in ["password", "creds", "credential"] if s in key_lower]):
            if any([True for extension in ["doc", "xls", "csv", "txt", "json"] if extension in key_lower]):
                suspicious = True
        #Bash or AWS files
        elif any([True for s in [".bash", ".aws"] if s in key_lower]):
            suspicious = True

        # Log as suspicious if not already done
        if suspicious:
            if msg.lower() in suspicious_files_found and not args.realert:
                return
            logger.log.critical("\n%s"%  (msg))
            add_string_to_file("%s/suspicious-files.txt" % (list_dir), string_to_add=msg)

    except:
        logger.log.warning("\nError on %s: %s" % (bucket_name, get_exception().replace("\n","")))


def suspicious_backup(key_lower):
    #Any database file
    if any([True for extension in [".sql", ".mysql", ".mongodb", ".mariadb", ".mdb", ".dump"] if extension in key_lower]):
        return True

    # Virtual drive backup
    if any([True for extension in [".vmdk", ".vbox", ".vhd", ".vdi", ".hdd"] if extension in key_lower]):
        return True

    #Compressed file
    if any([True for extension in [".gz", ".tar", ".zip", ".7z"] if extension in key_lower]):
        return True

    #Email backup
    if any([True for extension in [".pst", ] if extension in key_lower]):
        return True

    #Not a suspicious DB backup
    return False

