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
Miscellaneous utilities for Unicode handling.
"""

import sys
import locale
import unicodedata

from glob import glob as ascii_glob


class SysEncoding(object):
    """Character encodings used by this operating system.

    >>> print SysEncoding()
    {
        'command_line': 'cp437',
        'arguments': 'cp1252',
        'filenames': 'mbcs'
    }
    """

    def __init__(self):

        # Note: stream redirection as well as process piping
        # results in a "None" for the command line character
        # encoding, thus, fallback to ASCII.

        self.command_line = sys.stdin.encoding or \
                            sys.stdout.encoding or \
                            sys.stderr.encoding or \
                            'ascii'

        self.arguments = locale.getdefaultlocale()[1]
        self.filenames = sys.getfilesystemencoding()

    def __repr__(self):
        return repr({
            'arguments': self.arguments,
            'command_line': self.command_line,
            'filenames': self.filenames,
        })


def str2unicode(obj, encoding='utf-8'):
    """Convert string to Unicode using a given encoding."""
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return _normalize(obj)


def escape_unicode(text):
    """Convert Unicode to string with \\uXXXX and \\xXX escape sequences."""
    if isinstance(text, unicode):
        return repr(text)[2:-1]
    return text


def glob(pathname):
    """Glob pathnames with non-ASCII characters."""
    return _decode(ascii_glob(pathname), SysEncoding().filenames)


def argv(arguments=None):
    """Return list of arguments decoded with system character encoding."""
    arguments = sys.argv if arguments is None else arguments
    return _decode(arguments, SysEncoding().arguments)


def stdin():
    """Read standard input using system character encoding."""
    return _decode(sys.stdin.readlines(), SysEncoding().command_line)


def _decode(str_list, encoding):
    """Convert strings to Unicode using a given encoding."""
    decode = lambda text: str2unicode(text, encoding)
    return [decode(item) for item in str_list]


def _normalize(unistr):
    """Represent Unicode string with canonical composed form.

    Unicode has alternative representations called normalization forms,
    which means that e.g. "\\u017c" is the same character as "z\\u0307".

    Normalization ensures portability since e.g. filenames on Mac OS X
    are encoded with UTF-8 in NFD (decomposed), while Linux typically
    uses NFC for that purpose.
    """
    return unicodedata.normalize('NFC', unistr)
