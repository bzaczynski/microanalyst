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
# FITNESS FOR A PARTICULAR PURPOSE ANfD NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Generate xls summary with a vertical layout and open it.

Windows:
C:\\> type data.json | xlsv.py output.xls

Linux:
$ cat data.json | xlsv.py output.xls
"""

import sys

from microanalyst.xls import exporter, template


class VerticalTemplate(template.Template):
    """Template with all microplates kept in a single sheet."""

    def _render_data(self, workbook):

        sheet = workbook.add_sheet('Microplates')

        self.column_offset += 1 # account for a column with microplate name

        self._render_header(sheet)
        self._render_microplates(sheet)

        self._adjust_column_widths(sheet)

    def _render_microplates(self, sheet):
        for i, name in enumerate(self.model.microplate_names()):
            self._render_microplate(sheet, i, name)

    def _render_microplate(self, sheet, index, microplate_name):

        first_row = 1 + index * 96

        params = (sheet, first_row, microplate_name)
        self._render_microplate_name(*params)
        self._render_wells_and_genes_names(*params)
        self._render_values(*params)

    def _render_microplate_name(self, sheet, first_row, microplate_name):
        for i in xrange(96):
            sheet.write(first_row + i, 0, microplate_name)

    def _render_wells_and_genes_names(self, sheet, first_row, microplate_name):

        for i, well_name in enumerate(self.model.well_names()):

            if self.has_genes:
                sheet.write(first_row + i, 1, well_name)
            else:
                sheet.write(first_row + i, 1, well_name, self.styles('.header'))

            gene_name = self.model.gene(well_name, microplate_name)

            if gene_name:
                sheet.write(first_row + i, 2, gene_name, self.styles('.header'))

    def _render_values(self, sheet, first_row, microplate_name):

        values = self.model.values(microplate=microplate_name)
        column_index = self.column_offset

        for x, iteration in enumerate(values):
            for y, spreadsheet in enumerate(iteration):
                for w, value in enumerate(values[x, y]):

                    row_index = first_row + w
                    style = self._get_well_style(x, y, microplate_name, w, value)

                    sheet.write(row_index, column_index, value, style)
                column_index += 1

    def _adjust_column_widths(self, sheet):

        self._adjust_column_width(sheet, 0, self.model.microplate_names(), 2)
        self._adjust_column_width(sheet, 1, self.model.well_names(), 2)

        if self.has_genes:
            self._adjust_column_width(sheet, 2, self.genes, 3)


if __name__ == '__main__':
    try:
        exporter.Exporter(VerticalTemplate)
    except KeyboardInterrupt:
        print >> sys.stderr, 'Aborted'
