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
Helper for building control well mask.
"""

import numpy

from microanalyst.model import welladdr, spreadsheets
from microanalyst.model.commons import slice_or_index


class ControlMask(object):
    """Function object and a collection API over numpy array."""

    def __init__(self, json_data, microplate_names):
        self._mask = _process(json_data, microplate_names)
        self._microplate_names = microplate_names

    @property
    def values(self):
        """Numpy array of boolean values."""
        return self._mask

    def __call__(self,
                 iteration=None,
                 spreadsheet=None,
                 microplate=None,
                 well=None):
        """Return subarray of the mask or a scalar."""

        if microplate is not None:
            if not isinstance(microplate, int):
                microplate = self._microplate_names.index(microplate)

        x = slice_or_index(iteration)
        y = slice_or_index(spreadsheet)
        z = slice_or_index(microplate)
        w = slice_or_index(welladdr.indexof(well))

        return self._mask[x, y, z, w]

    def __getitem__(self, x):
        return self._mask[x]


def get_mask(json_data, microplate_names):
    """Return wrapper for numpy array."""
    return ControlMask(json_data, microplate_names)


def _process(json_data, microplate_names):
    """Return a 4d boolean numpy array or None."""

    if len(json_data[u'iterations']) > 0:

        assert spreadsheets.Spreadsheets(json_data).has_equal_number()

        mask_iterations = []
        for iteration in json_data[u'iterations']:
            mask_spreadsheets = []
            for spreadsheet in iteration[u'spreadsheets']:
                mask_microplates = []
                for microplate_name in microplate_names:

                    mask = [False] * 96

                    _update_mask(mask, microplate_name, iteration)
                    _update_mask(mask, microplate_name, spreadsheet)

                    mask_microplates.append(mask)

                mask_spreadsheets.append(mask_microplates)
            mask_iterations.append(mask_spreadsheets)

        return numpy.array(mask_iterations)


def _update_mask(mask, microplate_name, source):
    """Set flag for wells listed as control ones."""
    if u'control' in source:
        if microplate_name in source[u'control']:
            for well in source[u'control'][microplate_name]:
                mask[welladdr.indexof(well)] = True
