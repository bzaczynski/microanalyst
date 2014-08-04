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


class Spreadsheets(object):
    """Helper class for checking for missing spreadsheets."""

    def __init__(self, json_data):

        iterations = json_data[u'iterations']

        self._num_spreadsheets = [len(x[u'spreadsheets']) for x in iterations]
        self._max_spreadsheets = max(self._num_spreadsheets)
        self._min_spreadsheets = min(self._num_spreadsheets)

    def has_equal_number(self):
        """Check if each iteration has the same number of spreadsheets."""
        return self._min_spreadsheets == self._max_spreadsheets

    def num_missing(self, iteration_index):
        """Return the number of missing spreadsheets for an iteration."""
        num_spreadsheets = self._num_spreadsheets[iteration_index]
        return self._max_spreadsheets - num_spreadsheets

    @staticmethod
    def empty():
        """Return spreadsheet stub with no microplates nor filename."""
        return {u'filename': u'', u'microplates': {}}

