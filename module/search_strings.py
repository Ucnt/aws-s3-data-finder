#!/usr/bin/env python3
import multiprocessing
import itertools
import random, time
from lib.constants import *
from lib.arg_parser import *
from lib.logger import *
from lib.file_actions import *
from lib.progressbar import *
from module.run_bucket import run_bucket
from module.generate_strings import add_prefix_postfix


def string_gen_random(chars, num_chars):
    #Random chars
    while True:
        yield ''.join(random.choice(chars) for i in range(num_chars))


def string_gen_all(chars, num_chars):
    for index, value in enumerate(itertools.product(chars, repeat=num_chars)):
        yield "".join(value)


def search_strings():
    global buckets_checked

    #String generation check
    if args.all_chars:
        string_generator = string_gen_all(chars=args.characters, num_chars=args.num_chars)
        if args.start_after:
            while True:
                value = string_generator.__next__()
                if value == args.start_after:
                    break
    elif args.random_chars:
        string_generator = string_gen_random(chars=args.characters, num_chars=args.num_chars)

    progress = ProgressBar(num_items=0)

    active_processes = []            #Store the processes until they are done
    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size)

    #If you want to also run string generation, do it...otherwise just track results
    while True:
        #If able, add another process (keep plenty in the mix so it's not slow)
        if len(active_processes) < pool_size:
            try:
                next_bucket = string_generator.__next__()
                next_bucket_with_endpoint = "%s.%s" % (next_bucket, args.endpoint)
                if not args.rerun and next_bucket_with_endpoint.lower() in buckets_checked:
                    progress.num_skipped += 1
                    progress(num_completed=0, item=next_bucket)
                    if not args.prefix_postfix:
                        continue
                else:
                    active_processes.append(pool.apply_async(run_bucket, (next_bucket, )))
                    progress.num_items += 1

                #Add names with prefix/Postfix
                if args.prefix_postfix:
                    names_with_prefix_postfix = add_prefix_postfix(next_bucket)
                    for name_with_prefix_postfix in names_with_prefix_postfix:
                        name_with_prefix_postfix = name_with_prefix_postfix.lower()
                        if not args.rerun and "%s.%s" % (name_with_prefix_postfix, args.endpoint) in buckets_checked:
                            progress.num_skipped += 1
                            progress(num_completed=0, item=name_with_prefix_postfix)
                            continue    
                        active_processes.append(pool.apply_async(run_bucket, (name_with_prefix_postfix, )))
                        progress.num_items += 1

                        #Check running processes and remove them when done
                        for active_process in active_processes:
                            if active_process.ready():
                                try:
                                    buckets_checked.append("%s.%s" % (active_process._value.lower(), args.endpoint))
                                    add_string_to_file("%s/buckets-checked.txt" % (list_dir), string_to_add="%s.%s" % (active_process._value, args.endpoint))                           
                                except:
                                    pass
                                active_processes.remove(active_process)
                                progress(num_completed=1, item=active_process._value)
            except StopIteration:
                next_bucket = ""

        #Check running processes and remove them when done
        for active_process in active_processes:
            if active_process.ready():
                buckets_checked.append("%s.%s" % (active_process._value.lower(), args.endpoint))
                add_string_to_file("%s/buckets-checked.txt" % (list_dir), string_to_add="%s.%s" % (active_process._value, args.endpoint))
                active_processes.remove(active_process)
                progress(num_completed=1, item=active_process._value)


        if not active_processes and not next_bucket:
            break

    #DONE!
    progress.done()
    logger.log.critical("DONE!")


