#!/usr/env/bin python

import mimetypes
import os

custom_mimes = {
    'text/yaml': '.yml',
    'application/x-yaml': '.yml'
}

def guess_ext(mimetype):
    if mimetype in custom_mimes:
        return custom_mimes[mimetype]
    else:
        return mimetypes.guess_extension(mimetype)

