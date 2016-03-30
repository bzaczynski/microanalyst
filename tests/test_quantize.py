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

import json
import platform

from commons import ScriptTestCase
from microanalyst.commons.osutils import TempFile


class TestQuantize(ScriptTestCase):

    @classmethod
    def setUp(cls):
        cls.cat_program = 'type' if platform.system() == 'Windows' else 'cat'

    def test_default_values(self):

        CONTROL = 2
        OTHER = 1
        STARVED = 0

        with TempFile() as tmp:

            # given
            tmp.write(get_json_data())

            cat = [self.cat_program, tmp.name()]
            quantize = ['quantize.py']

            # when
            json_data = json.loads(self.pipe(cat, quantize))

            # then
            def values(iteration, spreadsheet, microplate):
                iteration = json_data['iterations'][iteration]
                spreadsheet = iteration['spreadsheets'][spreadsheet]
                microplate = spreadsheet['microplates'][microplate]
                return sorted(set(microplate['values']))

            self.assertListEqual([OTHER], values(0, 0, '001'))
            self.assertListEqual([STARVED], values(0, 0, '002'))
            self.assertListEqual([STARVED, OTHER], values(0, 1, '001'))
            self.assertListEqual([CONTROL], values(1, 0, '001'))
            self.assertListEqual([STARVED, OTHER, CONTROL], values(1, 0, '002'))

    def test_override_values(self):

        CONTROL = 333
        OTHER = 222
        STARVED = 111

        with TempFile() as tmp:

            # given
            tmp.write(get_json_data())

            cat = [self.cat_program, tmp.name()]
            quantize = ['quantize.py',
                        '--control', str(CONTROL),
                        '--other', str(OTHER),
                        '--starved', str(STARVED)]

            # when
            json_data = json.loads(self.pipe(cat, quantize))

            # then
            def values(iteration, spreadsheet, microplate):
                iteration = json_data['iterations'][iteration]
                spreadsheet = iteration['spreadsheets'][spreadsheet]
                microplate = spreadsheet['microplates'][microplate]
                return sorted(set(microplate['values']))

            self.assertListEqual([OTHER], values(0, 0, '001'))
            self.assertListEqual([STARVED], values(0, 0, '002'))
            self.assertListEqual([STARVED, OTHER], values(0, 1, '001'))
            self.assertListEqual([CONTROL], values(1, 0, '001'))
            self.assertListEqual([STARVED, OTHER, CONTROL], values(1, 0, '002'))

    def test_retun_integer_values(self):

        with TempFile() as tmp:

            # given
            tmp.write(get_json_data())

            cat = [self.cat_program, tmp.name()]
            quantize = ['quantize.py']

            # when
            json_data = json.loads(self.pipe(cat, quantize))

            # then
            for iteration in json_data['iterations']:
                for spreadsheet in iteration['spreadsheets']:
                    for microplate in spreadsheet['microplates'].values():
                        for value in microplate['values']:
                            self.assertIsInstance(value, int)

    def test_dont_pad_missing_spreadsheets_with_empty_stubs(self):

        with TempFile() as tmp:

            # given
            tmp.write(get_json_data())

            cat = [self.cat_program, tmp.name()]
            quantize = ['quantize.py']

            # when
            json_data = json.loads(self.pipe(cat, quantize))

            # then
            def num_spreadsheets(iteration):
                iteration = json_data['iterations'][iteration]
                return len(iteration['spreadsheets'])

            self.assertEqual(2, num_spreadsheets(0))
            self.assertEqual(1, num_spreadsheets(1))

    def test_retain_unknown_json_properties(self):

        with TempFile() as tmp:

            # given
            tmp.write(get_json_data())

            cat = [self.cat_program, tmp.name()]
            quantize = ['quantize.py']

            # when
            json_data = json.loads(self.pipe(cat, quantize))

            # then
            self.assertIn('foo', json_data)
            self.assertEqual('bar', json_data['foo'])


def get_json_data():
    return str(_json_data).replace("'", '"')


_json_data = {
    'foo': 'bar',
    'iterations': [
        {
            'spreadsheets': [
                {
                    'filename': 'iteration1/spreadsheet1.xls',
                    'microplates': {
                        '001': {
                            'values': [
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5
                            ]
                        },
                        '002': {
                            'values': [
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1
                            ]
                        }
                    }
                },
                {
                    'filename': 'iteration1/spreadsheet2.xls',
                    'microplates': {
                        '001': {
                            'values': [
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1
                            ]
                        }
                    }
                }
            ]
        },
        {
            'control': {
                '001': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12'],
                '002': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
            },
            'spreadsheets': [
                {
                    'filename': 'iteration2/spreadsheet1.xls',
                    'microplates': {
                        '001': {
                            'values': [
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5
                            ]
                        },
                        '002': {
                            'values': [
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.5,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1,
                                0.1
                            ]
                        }
                    }
                }
            ]
        }
    ]
}