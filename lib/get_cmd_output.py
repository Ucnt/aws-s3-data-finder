#!/usr/bin/env python3
import subprocess


def get_cmd_output(command):
    'Get output from a given command'
    p = subprocess.Popen(command,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            shell=True,)
    output, error = p.communicate()
    return output.decode('unicode_escape').strip()
