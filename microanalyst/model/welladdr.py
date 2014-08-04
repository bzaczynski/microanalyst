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
Utility functions for processing microplate's well addresses.
"""


def str2int(name):
    """Convert well address into a row-major index."""
    row = ord(name[0].upper()) - 65
    col = int(name[1:]) - 1

    assert 0 <= row < 8, 'Invalid well address "%s"' % name
    assert 0 <= col < 12, 'Invalid well address "%s"' % name

    return row*12 + col


def int2str(index):
    """Convert well index into a human readable address."""
    row = u'ABCDEFGH'[index / 12]
    col = (index % 12) + 1
    return u'%s%s' % (row, col)


def indexof(well):
    """Convert well address to index if string type provided."""
    return str2int(well) if isinstance(well, (str, unicode)) else well


def names():
    """Return well addresses in row-major order."""
    for row in u'ABCDEFGH':
        for col in xrange(1, 13):
            yield u'%s%d' % (row, col)
