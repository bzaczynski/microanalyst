#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2013 Bartosz Zaczynski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
OS-specific utilities.
"""

import os
import sys
import subprocess
import platform
import tempfile

from microanalyst.commons import uniutils


class TempFile(object):
    """Wrapper for tempfile with reasonable defaults."""

    def __init__(self, prefix='tmp'):
        self.obj = tempfile.NamedTemporaryFile(prefix=prefix, delete=False)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.delete()

    def name(self):
        return self.obj.name

    def write(self, text):
        self.obj.file.write(text)
        self.close()

    def close(self):
        self.obj.file.close()

    def delete(self):
        self.close()
        os.unlink(self.obj.name)


def open_with_default_app(filename):
    """Open the given filename with associated application."""

    os_name = platform.system()

    if os_name == 'Windows':
        os.startfile(filename)
    elif os_name == 'Linux':
        subprocess.call(('xdg-open', filename))
    elif os_name == 'Darwin':
        subprocess.call(('open', filename))
    else:
        print >> sys.stderr, 'Unknown operating system:', os_name


def expand(filenames):
    """Expand wild-cards in filenames (notably for Windows)."""

    result = []
    for filename in filenames:
        if u'*' in filename or u'?' in filename:
            result.extend(uniutils.glob(filename))
        else:
            result.append(filename)

    return result


def basename(path):
    """Wrapper for os.path.basename which has a bug on Linux."""
    return os.path.basename(path.replace(ur'\\', u'/').replace(u'\\', u'/'))
