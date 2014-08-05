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
Abstract representation of the experiment data used in microanalyst project.

Sample usage:
>>> import microanalyst.model
>>> model = microanalyst.model.from_file(r'data.json')
>>> model.values(microplate='B002', well='A4')
[[ 0.74559999  0.69270003  0.71609998]
 [ 0.75940001  0.71679997  0.70590001]
 [ 0.75809997  0.70069999  0.73320001]]
"""

import copy
import json

from microanalyst.model import welladdr
from microanalyst.model import control
from microanalyst.model.filenames import Filenames
from microanalyst.model.genes import Genes
from microanalyst.model.microplates import Microplates
from microanalyst.model.commons import get_array4d, slice_or_index


class Model(object):
    """High level interface for querying data model stored in JSON."""

    def __init__(self, json_data):

        self._data = copy.deepcopy(json_data) # prevent external side-effects
        self._filenames = Filenames(self.json_data)
        self._microplates = Microplates(self.json_data)

        microplate_names = self.microplate_names()

        self._genes = Genes(self, microplate_names)
        self._array4d = get_array4d(self.json_data, microplate_names)
        self._control_mask = control.get_mask(self.json_data, microplate_names)

    def __repr__(self):
        return '<microanalyst.model.Model object at %s>' % hex(id(self))

    @property
    def json_data(self):
        """Dictionary parsed from the JSON file."""
        return self._data

    @property
    def array4d(self):
        """Float array: iteration x spreadsheet x microplate x well."""
        return self._array4d

    @array4d.setter
    def array4d(self, value):
        """Float array: iteration x spreadsheet x microplate x well."""
        self._array4d = value

    @property
    def control_mask(self):
        """Boolean array denoting control wells at specific addresses."""
        return self._control_mask

    @property
    def num_iter(self):
        """Return number of iterations (series, clusters)."""
        return len(self._data[u'iterations'])

    @staticmethod
    def well_names():
        """Return well addresses in row-major order."""
        return welladdr.names()

    def microplate_names(self, iteration=None, spreadsheet=None):
        """Return a sorted list of microplates' names."""
        return self._microplates.get(iteration, spreadsheet)

    def filenames(self, with_path=True, iteration=None):
        """Return a list of spreadsheets' filenames in their original order."""
        return self._filenames.get(with_path, iteration)

    def gene(self, well, microplate):
        """Return gene name for a given (microplate, well) pair."""
        matched_genes = self.genes(well, microplate)
        return matched_genes[0] if len(matched_genes) > 0 else None

    def genes(self, well=None, microplate=None):
        """Return a sorted list of genes' names."""
        return self._genes.get(well, microplate)

    def genes_used(self):
        """Return a sorted list of genes' names used in the experiment."""
        return self._genes.get_used()

    def is_control(self, iteration, spreadsheet, microplate, well):
        return self.control_mask(iteration, spreadsheet, microplate, well)

    def values(self,
               iteration=None,
               spreadsheet=None,
               microplate=None,
               well=None):
        """Return subarray of values or a scalar.
           >>> model.values(microplate='001', well='A1')
           [[ 0.7385      0.66869998  0.66420001]
            [ 0.74629998  0.70660001  0.63870001]
            [ 0.71689999  0.78380001  0.72259998]]
        """

        if self.array4d is None:
            return None

        if microplate is not None:
            if not isinstance(microplate, int):
                microplate = self.microplate_names().index(microplate)

        x = slice_or_index(iteration)
        y = slice_or_index(spreadsheet)
        z = slice_or_index(microplate)
        w = slice_or_index(welladdr.indexof(well))

        return self.array4d[x, y, z, w]


def from_file(filename):
    """Return initialized instance of the Model."""
    with open(filename) as file_handle:
        return Model(json.load(file_handle))
