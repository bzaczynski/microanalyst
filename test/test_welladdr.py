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

import unittest

from microanalyst.model import welladdr


class TestNames(unittest.TestCase):

    def test_names_of_microplate_with_96_wells(self):

        # given
        expected = (
            'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12',
            'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12',
            'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12',
            'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12',
            'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12',
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
            'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12',
            'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12'
        )

        # when
        actual = tuple(welladdr.names())

        # then
        self.assertEqual(actual, expected)


class TestIllegalNames(unittest.TestCase):

    def test_a0(self):
        with self.assertRaises(AssertionError):
            welladdr.indexof('A0')

    def test_a13(self):
        with self.assertRaises(AssertionError):
            welladdr.indexof('A13')

    def test_h0(self):
        with self.assertRaises(AssertionError):
            welladdr.indexof('H0')

    def test_h13(self):
        with self.assertRaises(AssertionError):
            welladdr.indexof('H13')


class TestIndexToName(unittest.TestCase):

    def test_unicode(self):
        self.assertEqual(welladdr.indexof('A1'), welladdr.indexof(u'A1'))
        self.assertEqual(welladdr.indexof('A1'), 0)

    def test_well_name_at_first_index(self):
        self.assertEqual(welladdr.int2str(0), 'A1')

    def test_well_name_at_last_index(self):
        self.assertEqual(welladdr.int2str(95), 'H12')

    def test_well_name_in_first_row_and_last_column(self):
        self.assertEqual(welladdr.int2str(11), 'A12')

    def test_well_name_in_last_row_and_first_column(self):
        self.assertEqual(welladdr.int2str(84), 'H1')

    def test_index_out_of_upper_bound(self):
        with self.assertRaises(IndexError):
            welladdr.int2str(96)


class TestNameToIndex(unittest.TestCase):

    def test_names_are_case_insensitive(self):
        for name in welladdr.names():
            lowercase = welladdr.str2int(name.lower())
            uppercase = welladdr.str2int(name.upper())
            self.assertEqual(lowercase, uppercase)

    def test_first_name_is_at_index_0(self):
        self.assertEqual(welladdr.str2int('A1'), 0)

    def test_last_name_is_at_index_95(self):
        self.assertEqual(welladdr.str2int('H12'), 95)

    def test_well_name_in_first_row_and_last_column(self):
        self.assertEqual(welladdr.str2int('A12'), 11)

    def test_well_name_in_last_row_and_first_column(self):
        self.assertEqual(welladdr.str2int('H1'), 84)


if __name__ == '__main__':
    unittest.main()
