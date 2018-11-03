# Purpose
Find suspicious files (e.g. data backups, PII, credentials) across a large set of AWS S3 buckets and write the first 200k keys (by default) of listable buckets to a text file (in buckets/).

# Background
I had a repo (aws-s3-bruteforce) that was ugly code and would only identify buckets whose files you could list.  Instead, I wanted to look through those lists, at scale, and speficially look for potential data exposure.

# Overview
In module/run_bucket.py, each buckets' keys will be searched for a variety of items, e.g.:
- Potential database files (i.e. ".sql", ".mysql", ".mongodb", ".mariadb", ".mdb", ".dump") >= 50MB
- Potential backups (i.e. ".gz", ".tar", ".zip", ".7z") with "backup", "bak", or "archive" >= 50MB 
- Potential user data (i.e. "user", "member", "client") >= 50MB
- "password", "creds", "credential" in a "doc", "xls", "csv", "txt", or "json" file
- ".bash", ".aws"

# Requirements
- termcolor (to do CLI colors)
- awscli (needs to be configured with access and secret keys)

# Prefixes and postfixes
- For a bucket called "mycompany" a prefix or postfix would be something like "-admin" or ".admin"
- These are in module/prefixes_postfixes.py.  I have commented out a large number that were not useful to me.
- If a ".", "-", or "_" is already in the name, only that char will be used 

# Example commands

## Bruteforce single name

python3 find_data.py --bucket_name mybucket [-pp|--prefix_postfix]

## Bruteforce a list of names

python3 find_data.py --name_list list/buckets-to-check.txt [-pp|--prefix_postfix]

## Bruteforce character set

python3 find_data -c abcdefghijklmnopqrstuvwxyz --num_chars 3 --all_chars [-pp|--prefix_postfix] [-sa|--start_after] 
<br>
python3 find_data -c abcdefghijklmnopqrstuvwxyz --num_chars 3 --random_chars [-pp|--prefix_postfix]

## Test mode to see what bucket names would be tested (without running it)

python3 find_data.py --bucket_name mybucket [-pp|--prefix_postfix] --test

# Notes
- By default, bucket names already run will be skipped.  They can be re-run via "--rerun"
- Prior repo allowed a range of chars (e.g. 3-4 chars) to be run.  I will add this soon.
- By default, the first 200k keys will be looked at.  This can be modified via "--num_keys"
- Some buckets will error out.  list/bucket-errors.txt will list these buckets.  Often it will be JSON parsing issues.
