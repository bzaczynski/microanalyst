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

from microanalyst.model.commons import flatten


class Microplates(object):
    """Helper class for handling microplates' names."""

    def __init__(self, json_data):
        self.microplates = _process(json_data)

    def get(self, iteration, spreadsheet):
        """Return a sorted list of microplates' names."""

        if iteration is not None:
            if spreadsheet is not None:
                microplate_names = self.microplates[iteration][spreadsheet]
            else:
                microplate_names = flatten(self.microplates[iteration])
        else:
            if spreadsheet is not None:

                # ignore missing spreadsheets unless never found

                microplate_names = []
                for iteration in self.microplates:
                    if spreadsheet < len(iteration):
                        microplate_names.extend(iteration[spreadsheet])

                if len(microplate_names) == 0:
                    raise IndexError('list index out of range')
            else:
                microplate_names = flatten(self.microplates)

        return sorted(set(microplate_names))


def _process(json_data):
    """Return a 3d array (iteration x spreadsheet) of microplates' names."""

    iterations = []
    for iteration in json_data[u'iterations']:

        spreadsheets = []
        for spreadsheet in iteration[u'spreadsheets']:
            spreadsheets.append(spreadsheet[u'microplates'].keys())

        iterations.append(spreadsheets)

    return iterations
