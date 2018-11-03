#!/usr/bin/env python3
import ast
import sys
from lib.arg_parser import *
from lib.constants import *
from lib.logger import *
from lib.file_actions import *
from lib.get_cmd_output import *
from lib.traceback import *
min_db_mb = 50


def run_bucket(bucket_name):
    global checked_buckets
    try:
        #If you're just testing, print the bucket name and return
        if args.test:
            logger.log.critical("%s" % (bucket_name))
            return

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
            pass
        elif "AllAccessDisabled" in output:
            pass
        else:
            add_string_to_file("%s/buckets-found.txt" % (list_dir), string_to_add=bucket_name)
            output_json = ast.literal_eval(output.strip())
            #Write the bucket content to file (in case you want to look back later)
            if output_json['Contents']:
                add_string_to_file(file_name="%s/%s.txt" % (bucket_dir, bucket_name), string_to_add=output_json['Contents'])
            for item in output_json['Contents']:
                try:
                    key_lower = item['Key'].lower()
                    file_size_mb = int(item['Size']/1024/1024)
                    #Use the normal key name, not lower case
                    msg = "{file_size_mb} -> {bucket_name}.s3.amazonaws.com/{key}".format(file_size_mb=file_size_mb, bucket_name=bucket_name, key=item['Key'])
                    #Suspicious database/backup file
                    if suspicious_db_backup(key_lower) and file_size_mb >= min_db_mb:
                        logger.log.critical(msg)
                        add_string_to_file("%s/suspicious-files.txt" % (list_dir), string_to_add=msg)
                    #Potential credentials
                    elif any([True for s in ["password", "creds", "credential"] if s in key_lower]):
                        if any([True for extension in ["doc", "xls", "csv", "txt", "json"] if extension in key_lower]):
                            logger.log.critical(msg)
                            add_string_to_file("%s/suspicious-files.txt" % (list_dir), string_to_add=msg)
                    #Bash or AWS files
                    elif any([True for s in [".bash", ".aws"] if s in key_lower]):
                        logger.log.critical(msg)
                        add_string_to_file("%s/suspicious-files.txt" % (list_dir), string_to_add=msg)
                except:
                    logger.log.warning("Error on %s: %s" % (bucket_name, get_exception().replace("\n","")))

        #Mark as done... 
        checked_buckets.append(bucket_name)
        add_string_to_file("%s/buckets-checked.txt" % (list_dir), string_to_add=bucket_name)

    except:
        add_string_to_file("%s/buckets-errors.txt" % (list_dir), string_to_add=bucket_name)
        logger.log.warning("Error on %s: %s" % (bucket_name, get_exception().replace("\n","")))


def suspicious_db_backup(key):
    #Any database file
    if any([True for extension in [".sql", ".mysql", ".mongodb", ".mariadb", ".mdb", ".dump"] if extension in key]):
        return True

    #Compressed file
    if any([True for extension in [".gz", ".tar", ".zip", ".7z"] if extension in key]):
        #Backup
        if any([True for s in ["backup", "bak", "archive"] if s in key]):
            return True
        #Possible user data
        if any([True for s in ["user", "member", "client"] if s in key]):
            return True

    #Not a suspicious DB backup
    return False