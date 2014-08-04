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
import subprocess
import json

from commons import ScriptTestCase


class TestFileNames(ScriptTestCase):

    def test_retain_whitespace(self):

        # given
        filename = 'long filename with spaces'
        command = ['group.py', filename]

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertEqual(group[0]['files'][0], filename)

    def test_escape_unicode(self):
        try:
            # given
            filename = u'za\u017c\xf3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144'
            command = ['group.py', filename.encode(self.encoding.arguments)]

            # when
            output = self.execute(command)
            group = json.loads(output)

            # then
            self.assertIn(r'za\u017c\u00f3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144', output)
            self.assertEqual(group[0]['files'][0], filename)

        except UnicodeEncodeError:
            self.skip_due_to_encoding(self.encoding.arguments)

    def test_escape_windows_path_separator(self):

        # given
        command = ['group.py', 'root\parent\child']

        # when
        output = self.execute(command)
        group = json.loads(output)

        # then
        self.assertIn(r'root\\parent\\child', output)
        self.assertEqual(group[0]['files'][0], r'root\parent\child')

    def test_multiple_filenames(self):

        # given
        filenames = ['foo', 'bar', 'baz']
        command = ['group.py'] + filenames

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertEqual(group[0]['files'], filenames)

    def test_duplicate_filenames(self):

        # given
        filenames = ['foo', 'bar', 'foo', 'foo']
        command = ['group.py'] + filenames

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertEqual(group[0]['files'], filenames)

    def test_no_annotations(self):

        # given
        command = ['group.py', 'foo', 'bar', 'baz']

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertEqual(group[0].keys(), ['files'])


class TestAnnotations(ScriptTestCase):

    def test_no_whitespace_in_name(self):

        # given
        annotation_name = 'long annotation with whitespace'
        command = ['group.py', 'filename', '--' + annotation_name, 'dummy']

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertNotIn(annotation_name, group[0])

    def test_retain_whitespace_in_value(self):

        # given
        annotation_value = 'long annotation with whitespace'
        command = ['group.py', 'filename', '--annotation', annotation_value]

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertEqual(group[0]['annotation'], annotation_value)

    def test_escape_unicode_in_name(self):
        try:
            # given
            annotation = u'za\u017c\xf3\u0142\u0107'
            annotation_arg = (u'--' + annotation).encode(self.encoding.arguments)
            command = ['group.py', 'filename', annotation_arg, 'dummy']

            # when
            output = self.execute(command)
            group = json.loads(output)

            # then
            self.assertIn(r'"za\u017c\u00f3\u0142\u0107"', output)
            self.assertEqual(group[0][annotation], 'dummy')

        except UnicodeEncodeError:
            self.skip_due_to_encoding(self.encoding.arguments)

    def test_escape_unicode_in_value(self):
        try:
            # given
            value = u'g\u0119\u015bl\u0105 ja\u017a\u0144'
            value_arg = value.encode(self.encoding.arguments)
            command = ['group.py', 'filename', '--annotation', value_arg]

            # when
            output = self.execute(command)
            group = json.loads(output)

            # then
            self.assertIn(r'g\u0119\u015bl\u0105 ja\u017a\u0144', output)
            self.assertEqual(group[0]['annotation'], value)

        except UnicodeEncodeError:
            self.skip_due_to_encoding(self.encoding.arguments)

    def test_no_shadowing_of_files_attribute(self):

        # given
        command = ['group.py', 'filename', '--files', 'dummy']

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertEqual(group[0].keys(), ['files'])
        self.assertEqual(group[0]['files'], ['filename'])

    def test_single_dash(self):

        # given
        command = ['group.py', 'filename', '-a', 'dummy', '-foo', 'bar']

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertIn('files', group[0].keys())

        self.assertIn('a', group[0].keys())
        self.assertEqual(group[0]['a'], 'dummy')

        self.assertIn('foo', group[0].keys())
        self.assertEqual(group[0]['foo'], 'bar')

    def test_multiple_dashes(self):

        # given
        command = ['group.py', 'filename', '--a', 'dummy', '-----foo', 'bar']

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertIn('files', group[0].keys())

        self.assertIn('a', group[0].keys())
        self.assertEqual(group[0]['a'], 'dummy')

        self.assertIn('foo', group[0].keys())
        self.assertEqual(group[0]['foo'], 'bar')

    def test_duplicate_annotations(self):

        # given
        command = ['group.py',
                   'filename',
                   '--annotation', 'first',
                   '--annotation', 'second',
                   '--annotation', 'third']

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertEqual(group[0]['annotation'], 'third')

    def test_automatic_cast(self):

        # given
        command = ['group.py', 'filename',
                   '--int', '7',
                   '--float', '3.1415',
                   '--unicode', 'this is a Unicode string']

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertIsInstance(group[0]['int'], int)
        self.assertIsInstance(group[0]['float'], float)
        self.assertIsInstance(group[0]['unicode'], unicode)

    def test_ignore_missing_value(self):

        # given
        command = ['group.py', 'filename',
                   '--a1', 'v1',
                   '--a2', 'v2',
                   '--a3',
                   '--a4', 'v4']

        # when
        group = json.loads(self.execute(command))

        # then
        self.assertEqual(group[0]['a1'], 'v1')
        self.assertEqual(group[0]['a2'], 'v2')
        self.assertEqual(group[0]['a3'], '--a4')
        self.assertNotIn('a4', group[0])


class TestPipe(ScriptTestCase):

    def setUp(self):

        self.raw_result = self.pipe(
            ['group.py', 'Jetsons', 'Flintstones', 'Adams', '--type', 'cartoon'],
            ['group.py', 'apple', 'banana', 'orange', '--fresh', 'true', '--other', 'healthy'],
            ['group.py', 'Opel', 'Audi', 'Peugeot', 'Fiat', '--continent', 'Europe', '--car', 'small']
        )

        self.result = json.loads(self.raw_result)

    def test_return_list(self):
        self.assertIsInstance(self.result, list)

    def test_retain_number_of_groups(self):
        self.assertEqual(len(self.result), 3)

    def test_retain_order_of_groups(self):
        for i, item in enumerate(['Jetsons', 'orange', 'Audi']):
            self.assertIn(item, self.result[i]['files'])

    def test_retain_order_of_filenames(self):
        self.assertEqual(self.result[0]['files'], ['Jetsons', 'Flintstones', 'Adams'])
        self.assertEqual(self.result[1]['files'], ['apple', 'banana', 'orange'])
        self.assertEqual(self.result[2]['files'], ['Opel', 'Audi', 'Peugeot', 'Fiat'])

    def test_retain_annotations(self):

        self.assertEqual(self.result[0]['type'], 'cartoon')

        self.assertEqual(self.result[1]['fresh'], 'true')
        self.assertEqual(self.result[1]['other'], 'healthy')

        self.assertEqual(self.result[2]['continent'], 'Europe')
        self.assertEqual(self.result[2]['car'], 'small')

    def test_pretty_print(self):
        expected = json.dumps(self.result, indent=4).strip()
        actual = self.raw_result.strip().replace('\r', '')
        self.assertEqual(actual, expected)


class TestNegative(ScriptTestCase):

    def test_too_few_arguments(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.execute('group.py', stderr=subprocess.STDOUT)


if __name__ == '__main__':
    unittest.main()
