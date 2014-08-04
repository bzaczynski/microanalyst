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
Helper functions used across the model.
"""

import sys
import numpy

from microanalyst.model.spreadsheets import Spreadsheets


def slice_or_index(index):
    """Return index or slice the array [:]."""
    return slice(None) if index is None else index


def flatten(sequence):
    """Recursively remove None values and expand nested sequences."""

    result = []
    for item in sequence:
        if item is not None:
            if is_sequence(item):
                result.extend(flatten(item))
            else:
                result.append(item)

    return result


def is_sequence(obj):
    """Check if an object is a sequence but not a string."""
    return isinstance(obj, (list, tuple, numpy.ndarray))


def get_array4d(json_data, microplate_names):
    """Return well values as numpy' 4d array.

       (iteration x spreadsheet x microplate x well)
    """

    if len(json_data[u'iterations']) > 0:

        pad_missing_spreadsheets(json_data)

        iterations = []
        for iteration in json_data[u'iterations']:
            spreadsheets = []
            for spreadsheet in iteration[u'spreadsheets']:
                spreadsheet_microplates = spreadsheet[u'microplates']
                microplates = []
                for microplate_name in microplate_names:
                    if microplate_name in spreadsheet_microplates:
                        microplate = spreadsheet_microplates[microplate_name]
                        microplates.append(microplate[u'values'])
                    else:
                        microplates.append([None]*96)
                spreadsheets.append(microplates)
            iterations.append(spreadsheets)

        return numpy.array(iterations)


def pad_missing_spreadsheets(json_data):
    """Append stubs for missing spreadsheets to JSON."""

    spreadsheets = Spreadsheets(json_data)

    if not spreadsheets.has_equal_number():

        print >> sys.stderr, \
            'Warning: unequal number of spreadsheets across iterations'

        for i, iteration in enumerate(json_data[u'iterations']):
            padding = [Spreadsheets.empty()] * spreadsheets.num_missing(i)
            iteration[u'spreadsheets'].extend(padding)
