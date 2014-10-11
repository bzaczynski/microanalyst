#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2013, 2014 Bartosz Zaczynski
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

import sys
import numpy

from microanalyst.model import welladdr
from microanalyst.model.commons import flatten, slice_or_index


class Gene(str):
    """Gene name and its associated (microplate, well) pair."""

    def __new__(cls, model, name, well, microplate):
        return str.__new__(cls, name)

    def __init__(self, model, name, well, microplate):

        super(Gene, self).__init__()

        self.model = model
        self.name = name
        self.well_name = well
        self.microplate_name = microplate

    def __call__(self):
        return (self.microplate_name, self.well_name)

    def values(self, iteration=None, spreadsheet=None):
        """Return data samples corresponding to a gene.
           >>> gene.values()
           [[ 0.7385      0.66869998  0.66420001]
            [ 0.74629998  0.70660001  0.63870001]
            [ 0.71689999  0.78380001  0.72259998]]
        """
        return self.model.values(iteration=iteration,
                                 spreadsheet=spreadsheet,
                                 microplate=self.microplate_name,
                                 well=self.well_name)


class Genes(object):
    """Helper class for handling genes' names."""

    def __init__(self, model, microplate_names):

        if not u'genes' in model.json_data:
            self.genes_matrix = None
        else:

            genes_json = model.json_data[u'genes']

            self.microplate_names = microplate_names
            self.microplate_names_with_genes = sorted(set(genes_json))
            self.indexof = {
                x: i for i, x in enumerate(self.microplate_names_with_genes)
            }

            self.genes_matrix = self._process(model, genes_json)

            self.genes = {}
            for gene in self.genes_matrix.ravel():
                if gene:
                    gene_name = gene.name.lower()
                    if gene_name in self.genes:
                        self.genes[gene_name].append(gene)
                    else:
                        self.genes[gene_name] = [gene]

            self._check_duplicates()

    def get_by_name(self, name):
        """Get gene by its name (case insensitive)."""

        name = name.lower()

        if name in self.genes:
            return self.genes[name][0]
        else:
            return None

    def get(self, well, microplate):
        """Return a sorted list of genes' names."""

        if self.genes_matrix is None:
            return []

        if microplate is None:
            x = slice_or_index(None)
        else:
            if microplate in self.microplate_names_with_genes:
                x = slice_or_index(self.indexof[microplate])
            else:
                if microplate in self.microplate_names:
                    return []
                else:
                    raise KeyError('Unknown microplate "%s"' % microplate)

        y = slice_or_index(welladdr.indexof(well))

        if not (well is None or microplate is None):
            return flatten([self.genes_matrix[x, y]])
        else:
            return sorted(set(flatten(self.genes_matrix[x, y])))

    def get_used(self):
        """Return a sorted list of genes' names used in the experiment."""

        if self.genes_matrix is None:
            return []

        genes = []
        for name in self.microplate_names:
            genes.extend(self.get(microplate=name, well=None))

        return sorted(set(genes))

    def _process(self, model, genes_json):
        """Return a 2d array (microplate x well) of gene names."""

        microplates = []
        for microplate in self.microplate_names_with_genes:
            wells = []
            for well in welladdr.names():
                if well in genes_json[microplate]:
                    name = genes_json[microplate][well]
                    wells.append(Gene(model, name, well, microplate))
                else:
                    wells.append(None)
            microplates.append(wells)

        return numpy.array(microplates)

    def _check_duplicates(self):
        """Warn about duplicate instances of genes on microplates."""

        duplicates = set()
        for name in self.genes:
            if len(self.genes[name]) > 1:
                duplicates.add(name)

        for name in sorted(duplicates):

            original_name = self.genes[name][0].name
            instances = ['("%s"/%s)' % (
                x.microplate_name, x.well_name) for x in self.genes[name]
            ]

            message = 'Warning: duplicate gene "%s" at %s'
            print >> sys.stderr, message % (original_name, ', '.join(instances))
