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

import numpy
import itertools

from microanalyst.xls import stylesheet
from microanalyst.model import thresholds


class Template(object):
    """Base template for output xls file."""

    CHAR_WIDTH = 256

    DEFAULT_STYLE = """
        * {
            border-color: gray25;
        }

        .default, .one {
        }

        .alt {
            background-color: ivory;
        }

        .header {
            font-weight: bold;
        }

        .centered, .binary {
            text-align: center;
        }

        .binary {
            number-format: 0;
        }

        .starved, .control, .violated, .other {
            color: white;
        }

        .starved {
            background-color: black;
        }

        .control {
            background-color: dark_red;
        }

        .violated {
            background-color: red;
        }

        .other {
            background-color: red;
        }

        .infected, .zero {
            background-color: lime;
            color : dark_green;
        }
    """

    def __init__(self, model, css_filename=None, colors=False, binary=False):

        self.model = model
        self.genes = model.genes()
        self.has_genes = len(self.genes) > 0
        self.column_offset = 2 if self.has_genes else 1

        self.colors_enabled = colors
        self.binary_enabled = binary

        self.styles = stylesheet.parse(Template.DEFAULT_STYLE)

        if css_filename:
            self.styles.override(stylesheet.load(css_filename))

        if self.binary_enabled:

            def has_no_background(style_name):
                return not 'background-color' in self.styles.peek(style_name)

            self.alt_one = has_no_background('.one')
            self.alt_zero = has_no_background('.zero')
            self.alt_other = has_no_background('.other')

        self.is_starved,\
        self.is_infected,\
        self.is_violated = thresholds.default()

    def render(self, workbook):
        """Fill spreadsheet with values from the model."""

        if self.colors_enabled and not self.binary_enabled:
            self._render_legend(workbook)

        self._render_data(workbook)

    def _render_header(self, sheet):
        """Write spreadsheet filenames at the top."""

        column_index = self.column_offset

        for i in xrange(self.model.num_iter):
            for filename in self.model.filenames(with_path=False, iteration=i):

                style = self.styles('.header',
                                    alt=i % 2,
                                    binary=self.binary_enabled)

                sheet.write(0, column_index, filename, style)
                self._set_column_width(sheet, column_index, filename)

                column_index += 1

    def _render_data(self, workbook):
        """Template method to be implemented in subclasses."""
        raise NotImplementedError()

    def _render_legend(self, workbook):
        """Explain the meaning of colors used in the spreadsheet."""

        sheet = workbook.add_sheet('Legend')

        # header
        sheet.write(0, 0, 'Predicate', self.styles('.header'))
        sheet.write(0, 1, 'Meaning', self.styles('.header'))

        # body
        starvation, infection, violation = [
            str(x) for x in thresholds.default()
        ]

        for i, (predicate, meaning, style) in enumerate([
            (starvation, 'starved', self.styles('.starved')),
            (infection, 'infected', self.styles('.infected')),
            (violation, 'control violated', self.styles('.violated')),
            ('N/A', 'control fine', self.styles('.control'))
        ]):
            sheet.write(1 + i, 0, predicate, self.styles('.centered'))
            sheet.write(1 + i, 1, meaning, style)

        self._set_column_width(sheet, 1, 'control violated')

    def _get_well_style(self, iteration, spreadsheet, microplate, well, value):

        if value is not None and self.colors_enabled:

            if self.binary_enabled:

                def get_binary_style(suffix, alt_flag):
                    return self.styles('.binary%s' % suffix,
                                       alt=(iteration % 2) and alt_flag)

                if value == 0:
                    return get_binary_style('.zero', self.alt_zero)
                elif value == 1:
                    return get_binary_style('.one', self.alt_one)
                else:
                    return get_binary_style('.other', self.alt_other)
            else:

                if self.model.is_control(iteration,
                                         spreadsheet,
                                         microplate,
                                         well):
                    if self.is_violated(value):
                        return self.styles('.violated')
                    else:
                        return self.styles('.control')
                else:
                    if self.is_starved(value):
                        return self.styles('.starved')
                    elif self.is_infected(value):
                        return self.styles('.infected')

        return self.styles('.default',
                           alt=iteration % 2,
                           binary=self.binary_enabled)

    def _adjust_column_width(self, sheet, column, values, padding=0):
        longest_name = max(values, key=len)
        self._set_column_width(sheet, column, longest_name + 'W'*padding)

    @staticmethod
    def _set_column_width(sheet, column_index, text):
        """Set width of a spreadsheet column to accomodate the given text."""
        sheet.col(column_index).set_width(len(text)*Template.CHAR_WIDTH)
