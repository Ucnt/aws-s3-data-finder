# Purpose
Find suspicious files (e.g. data backups, PII, credentials) across a large set of AWS S3 buckets and write the first 200k keys (by default) of listable buckets to a .json or .xml file (in buckets/) via awscli OR unauthenticated via HTTP requests.

# Reason
Companies and individuals, far too often, have public S3 buckets with client data or PII in them.

# Background
I had a repo (aws-s3-bruteforce) that was ugly, Python2 code and would only identify buckets whose files you could list.  Instead, I wanted to look through those lists, at scale, and speficially look for potential data exposure.

# Overview
In module/run_bucket.py, each buckets' keys will be searched for a variety of items, i.e.:
- Potential database files (i.e. ".sql", ".mysql", ".mongodb", ".mariadb", ".mdb", ".dump") >= 50MB
- Potential backups (i.e. ".gz", ".tar", ".zip", ".7z") with "backup", "bak", or "archive" >= 50MB 
- Potential user data (i.e. "user", "member", "client") >= 50MB
- "password", "creds", "credential" in a "doc", "xls", "csv", "txt", or "json" file
- ".bash", ".aws"
<br>
If one of the above file types are found, they will be written written to the screen and to list/suspicious-files.txt in the format (size -> file_link)
<br><br>
Buckets found (both public and authenticated) will be written to list/buckets-found

# Requirements (in requirements.txt)
- termcolor (to do CLI colors)
- awscli (for auth scans, needs to be configured with access and secret keys)
- Install via sudo -H pip3 install -r requirements.txt

# Prefixes and postfixes
- For a bucket called "mycompany" a prefix or postfix would be something like "-admin" or ".admin"
- These are in module/prefixes_postfixes.py.  I have commented out a large number that were not useful to me.
- If a ".", "-", or "_" is already in the name, only that char will be used (faster and best results)
- The --prefix_postfix option can be: both, prefix, or postfix
- You can add "{separator}" to a prefix/postfix in module/prefixes_postfixes.py e.g. "zoom{separator}meetings".  This will, as the script goes through separators (e.g. "-", "_", "."), that separator will be added in place if "{separator}".  This makes it less work to add variations of prefixes/postfixes with consistent character types.  In the script this will add "zoommeetings" "zoom-meetings" "zoom_meetings" and "zoom.meetings" as a prefix/postfix.

# Example commands

## Run a single bucket UNAUTHENTICATED

python3 find_data.py -n bucketname -u

## Run a single bucket UNAUTHENTICATED but DO NOT follow redirects (by default, it will)

python3 find_data.py -n bucketname -u --no_follow_redirect

## Bruteforce single name (bucket name or company name)

python3 find_data.py --bucket_name mybucket [-pp|--prefix_postfix OPTION]

## Bruteforce a list of names (bucket name or company name)

python3 find_data.py --name_list list/buckets-to-check.txt [-pp|--prefix_postfix OPTION]

## Bruteforce character set

python3 find_data -c abcdefghijklmnopqrstuvwxyz --num_chars 3 --all_chars [-pp|--prefix_postfix OPTION] [-sa|--start_after] 
<br>
python3 find_data -c abcdefghijklmnopqrstuvwxyz --num_chars 3 --random_chars [-pp|--prefix_postfix OPTION]

## Test mode to see what bucket names would be tested (without running it)

python3 find_data.py --bucket_name mybucket [-pp|--prefix_postfix OPTION] --test

## Run Unauth requests via a different endpoint (defaulted to "s3.amazonaws.com")

python3 find_data.py -n bucketname -u -e "s3.us-east-2.amazonaws.com"
<br>
** IF YOU DO THIS, EITHER RUN IT UNAUTHENTICATED OR CHANGE YOUR AWSCLI DEFAULT ENDPOINT!!


# Notes
- By default, bucket names already run will be skipped.  They can be re-run via "--rerun"
- By default, files already alerted on will not be alerted again.  You can get re-alerted by adding "--realert"
- Prior repo allowed a range of chars (e.g. 3-4 chars) to be run.  I will add this soon.
- By default, the first 200k keys will be looked at.  This can be modified via "--num_keys"
- Some buckets will error out.  list/bucket-errors.txt will list these buckets.  Often it will be JSON parsing issues.
- If doing company names, use the --prefix_postrix option to format it, e.g. "my company" to "mycompany"

# AWS Account and Access/Secret Key Instructions
- Setup an AWS Account (https://portal.aws.amazon.com/billing/signup)
- Create an AWS user (https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html)
- Create access keys and secret keys (https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)
