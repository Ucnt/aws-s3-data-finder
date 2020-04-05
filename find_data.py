#!/usr/bin/env python3
import multiprocessing
import random, time
import ast
from lib.logger import *
from lib.progressbar import *
from lib.file_actions import *
from lib.get_cmd_output import *
from module.run_bucket import run_bucket
from module.search_strings import search_strings
from module.generate_strings import add_prefix_postfix


if __name__ == "__main__":
    global buckets_checked
    logger.log.critical("Running with args: %s" % (args))

    if len(buckets_checked) > 1:
        logger.log.critical('''
******************************************************************************
YOU HAVE {} checked buckets that you are going to look through to see if you re-run.
THIS COULD HAVE A SIGNIFICANT impact on performance.
**********************************************************************************
'''.format(len(buckets_checked)))

    if args.endpoint and not args.unauthenticated:
        logger.log.critical('''
********************************************************************************************
************************************************************************************************
Running on %s.  BE SURE AWS CLI IS CONFIGURED FOR IT!!
************************************************************************************************
************************************************************************************************
''' % (args.endpoint))

    active_processes = []            #Store the processes until they are done
    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size)
    progress = ProgressBar(num_items=0)

    #If chars are given, you want to do a brute-force 
    if args.characters:
        if not args.num_chars:
            logger.log.critical("Must give the number of chars for the bucket name via --num_chars")
        elif not args.all_chars and not args.random_chars:
            logger.log.critical("No valid search type (--all_chars or --random_chars) was given")
        else:
            search_strings()

    #Just run one name
    elif args.bucket_name:
        #Run run prefixes and postfixes, if you want...
        if args.prefix_postfix:
            names_with_prefix_postfix = add_prefix_postfix(args.bucket_name)
            for name_with_prefix_postfix in names_with_prefix_postfix:
                active_processes.append(pool.apply_async(run_bucket, (name_with_prefix_postfix, )))
                progress.num_items += 1
        else:
            #Run the given bucket name
            active_processes.append(pool.apply_async(run_bucket, (args.bucket_name, )))
            progress.num_items += 1

    #Run a list of names
    elif args.name_list:
        buckets_to_check = list_from_lines(args.name_list)

        #Add given buckets to asynch pool
        last_active_process = ""       
        for bucket_to_check in buckets_to_check:
            #Add names with prefix/Postfix
            if args.prefix_postfix:
                names_with_prefix_postfix = add_prefix_postfix(bucket_to_check)
                for name_with_prefix_postfix in names_with_prefix_postfix:
                    #Skip here so you don't have to hit the multiprocess delay
                    bucket_with_endpoint = "%s.%s" % (name_with_prefix_postfix, args.endpoint)
                    if not args.rerun and bucket_with_endpoint.lower() in buckets_checked:
                        progress.num_skipped += 1
                        continue
                    progress.num_items += 1
                    progress(num_completed=0, item=last_active_process)
                    active_processes.append(pool.apply_async(run_bucket, (name_with_prefix_postfix, )))

                    #Go through and check if any processes are done
                    #for active_process in active_processes:
                    #    if active_process.ready():
                    #        active_processes.remove(active_process)
                    #        last_active_process = active_process._value
                    #        progress(num_completed=1, item=last_active_process)
            else:
                #Skip here so you don't have to hit the multiprocess delay
                bucket_with_endpoint = "%s.%s" % (bucket_to_check, args.endpoint)
                if not args.rerun and bucket_with_endpoint.lower() in buckets_checked:
                    progress.num_skipped += 1
                    progress(num_completed=0, item=last_active_process)
                    continue
                active_processes.append(pool.apply_async(run_bucket, (bucket_to_check, )))
                progress.num_items += 1

            #Keep track of progress...
            for active_process in active_processes:
                if active_process.ready():
                    buckets_checked.append("%s.%s" % (active_process._value.lower(), args.endpoint))
                    add_string_to_file("%s/buckets-checked.txt" % (list_dir), string_to_add="%s.%s" % (active_process._value, args.endpoint))                      
                    active_processes.remove(active_process)
                    last_active_process = active_process._value                   
                    progress(num_completed=1, item=last_active_process)
            #Be sure something shows if you're just skipping buckets
            if not last_active_process:
                progress(num_completed=0, item=bucket_to_check)


    #Keep checkig on progress until you're
    while True:
        #Check running processes and remove them when done
        for active_process in active_processes:
            if active_process.ready():
                add_string_to_file("%s/buckets-checked.txt" % (list_dir), string_to_add="%s.%s" % (active_process._value, args.endpoint))                  
                active_processes.remove(active_process)
                progress(num_completed=1, item=active_process._value)

        if not active_processes:
            progress.done()
            break

        time.sleep(.05)

