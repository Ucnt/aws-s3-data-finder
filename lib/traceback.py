#!/usr/bin/env python3
import os, sys, traceback


def get_exception():
    """Return the full tracebacko of the error"""
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    return '''Error Traceback:
Python Version: {version}
File: {file_name}
Error Type: {error_type}
Error Message: {error_message}
{traceback}'''.format(
                    version =sys.version.split("(")[0],
                    file_name = fname,
                    error_type = exc_type.__name__,
                    error_message = exc_obj,
                    traceback = traceback.format_exc().replace(" (most recent call last)","").split("TypeError")[0].strip()
                    )
