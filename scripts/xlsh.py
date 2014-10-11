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
Generate xls summary with a horizontal layout and open it.

Windows:
C:\\> type data.json | xlsh.py output.xls

Linux:
$ cat data.json | xlsh.py output.xls
"""

import sys

from microanalyst.xls import exporter, template


class HorizontalTemplate(template.Template):
    """Template with microplates kept in separate sheets."""

    def _render_data(self, workbook):
        for name in self.model.microplate_names():
            self._render_microplate(workbook, name)

    def _render_microplate(self, workbook, microplate_name):

        sheet = workbook.add_sheet(microplate_name)

        self._render_header(sheet)
        self._render_wells_and_genes_names(sheet, microplate_name)
        self._render_values(sheet, microplate_name)

        self._adjust_column_widths(sheet)

    def _render_wells_and_genes_names(self, sheet, microplate_name):

        for i, well_name in enumerate(self.model.well_names()):

            if self.has_genes:
                sheet.write(1 + i, 0, well_name)
            else:
                sheet.write(1 + i, 0, well_name, self.styles('.header'))

            gene_name = self.model.gene_at(well_name, microplate_name)

            if gene_name:
                sheet.write(1 + i, 1, gene_name, self.styles('.header'))

    def _render_values(self, sheet, microplate_name):

        values = self.model.values(microplate=microplate_name)
        column_index = self.column_offset

        for x, iteration in enumerate(values):
            for y, spreadsheet in enumerate(iteration):
                for w, value in enumerate(values[x, y]):

                    row_index = 1 + w
                    style = self._get_well_style(x, y, microplate_name, w, value)

                    sheet.write(row_index, column_index, value, style)
                column_index += 1

    def _adjust_column_widths(self, sheet):

        self._adjust_column_width(sheet, 0, self.model.well_names(), 2)

        if self.has_genes:
            self._adjust_column_width(sheet, 1, self.genes, 3)


if __name__ == '__main__':
    try:
        exporter.Exporter(HorizontalTemplate)
    except KeyboardInterrupt:
        print >> sys.stderr, 'Aborted'
