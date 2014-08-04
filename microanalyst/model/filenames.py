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

from microanalyst.commons import osutils
from microanalyst.model.commons import flatten


class Filenames(object):
    """Helper class for filename handling."""

    def __init__(self, json_data):
        self.filenames = _process(json_data)

    def get(self, with_path, iteration):
        """Return a flat list of filenames in their original order."""

        def normalize(filenames):
            if not with_path:
                return [osutils.basename(x) for x in filenames]
            return filenames

        if iteration is not None:
            return normalize(list(self.filenames[iteration]))
        else:
            return normalize(flatten(self.filenames))


def _process(json_data):
    """Return a list of filenames grouped by iteration."""

    iterations = []
    for iteration in json_data[u'iterations']:
        filenames = [x[u'filename'] for x in iteration[u'spreadsheets']]
        iterations.append(filenames)

    return iterations
