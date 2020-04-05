#!/usr/bin/env python3
from module.prefixes_postfixes import *
from lib.arg_parser import *
entities = [
                " Inc", " incorporated", 
                " Co", "company", 
                " Corp", " Corporation"
                " LLC",
                " Ltd", "Limited",
                " Group",
                " Holding",
                " Services",
                " Technologies", " Tech",
           ]


def add_prefix_postfix(bucket_name):
    bucket_name = bucket_name.lower()
    bucket_names = remove_junk_chars(bucket_name)
    add_with_no_entity(bucket_names)
    add_with_space_replacements(bucket_names)

    separator_in_name = ""
    for bucket in bucket_names:
        for prefix_postfix_separator in prefix_postfix_separators:
            if (prefix_postfix_separator in bucket and prefix_postfix_separator != ""):
                separator_in_name = prefix_postfix_separator
                break

    names_with_additions = []
    for bucket in bucket_names:
        for prefix_postfix_separator in prefix_postfix_separators:
            #Only add teh separator if it's in the bucket name already or there aren't any separators
            if (separator_in_name == prefix_postfix_separator or not separator_in_name):
                for prefix_postfix in prefixes_postfixes:
                    if "{separator}" in prefix_postfix.lower():
                        prefix_postfix = prefix_postfix.replace("{separator}", prefix_postfix_separator)
                    if args.prefix_postfix.lower() in ['both', 'prefix']:
                        names_with_additions.append("{prefix_postfix}{prefix_postfix_separator}{bucket}".format(prefix_postfix=prefix_postfix, prefix_postfix_separator=prefix_postfix_separator, bucket=bucket))
                    if args.prefix_postfix.lower() in ['both', 'postfix']:
                        names_with_additions.append("{bucket}{prefix_postfix_separator}{prefix_postfix}".format(bucket=bucket, prefix_postfix_separator=prefix_postfix_separator, prefix_postfix=prefix_postfix))

    return list(set(names_with_additions))


def remove_junk_chars(bucket_name):
    """Remove characters that shouldn't or won't be in a bucket name"""
    name = bucket_name
    names = []

    #Remove junk chars
    junk_chars = ["'", '"', "&#39;", "!"]
    for junk_char in junk_chars:
        name = name.replace(junk_char, "")

    #Remove domains (this can be added later)
    domains = [".com", ".org", ".net", ".edu", ".gov"]
    for domain in domains:
        name = name.replace(domain, "")

    #Replace junk char with space so it can be replaced by a replacement char
    name = name.replace(","," ")
    name = name.replace("."," ")
    name = name.replace("*"," ")
    name = name.replace("&", " and ")

    #Remove any duplicate spaces
    while "  " in name:
        name = name.replace("  ", " ")

    #Add the name without "and" if it's there (e.g. "Bob & Sue" becomes "Bob and Sue" and "Bob Sue")
    names.append(name.strip())
    if " and " in name:
        names.append(name.replace(" and ", " ").strip())
    return names


def add_with_space_replacements(bucket_names):
    """Replaces every space in the line with replacements, e.g. -,_, and null"""
    space_replaced_names = []
    names_to_remove = []

    for name in bucket_names:
        if " " in name:
            for space_replacement in prefix_postfix_separators:
                space_replaced_names.append(name.replace(" ",space_replacement).strip())
            names_to_remove.append(name)

    #Remove all instances of names with spaces
    for name_to_remove in names_to_remove:
        while name_to_remove in bucket_names:
            bucket_names.remove(name_to_remove)

    bucket_names.extend(space_replaced_names)


def add_with_no_entity(names):
    """If an entity name, e.g. Inc. or Corp., is in the name, add the name without it"""
    chomped_names = []
    for name in names:
        for entity in entities:
            if entity.lower() in name:
                chomped_names.append(rchop(name, entity.lower()).strip())
    names.extend(chomped_names)


def rchop(thestring, ending):
    """Removes the given ending from the end of the string"""
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    return thestring