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

import platform
import unittest
import json

from commons import ScriptTestCase
from microanalyst.commons.osutils import TempFile


class TestFileNames(ScriptTestCase):

    def test_accept_whitespace(self):

        filename = 'long filename with spaces'

        with TempFile(filename) as tmp:

            # given
            tmp.write('{"foo":"bar"}')

            echo = ['echo', '[{}]']
            control = ['control.py', tmp.name()]

            # when
            result = json.loads(self.pipe(echo, control))

            # then
            self.assertIn('control', result[0])
            self.assertIn('foo', result[0]['control'])
            self.assertEqual(result[0]['control']['foo'], 'bar')

    def test_accept_unicode(self):
        try:
            filename = u'za\u017c\xf3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144'

            with TempFile(filename) as tmp:

                # given
                tmp.write('{"foo":"bar"}')

                echo = ['echo', '[{}]']
                control = ['control.py', tmp.name()]

                # when
                result = json.loads(self.pipe(echo, control))

                # then
                self.assertIn('control', result[0])
                self.assertIn('foo', result[0]['control'])
                self.assertEqual(result[0]['control']['foo'], 'bar')

        except UnicodeEncodeError:
            self.skip_due_to_encoding(self.encoding.arguments)


@unittest.skipIf(platform.system() == 'Windows', 'Popen cannot handle double quotes on Windows')
class TestContents(ScriptTestCase):

    # On Windows subprocess.Popen uses subprocess.list2cmdline() to
    # convert argument list to a string. However, it always escapes
    # double quotes while they are part of the test.

    def test_no_shadowing_of_control_attribute(self):

        with TempFile() as tmp:

            # given
            tmp.write('{"foo":"bar"}')

            echo = ['echo', '[{"control":"dummy"}]']
            control = ['control.py', tmp.name()]

            # when
            stdout, stderr = self.pipe_with_stderr(echo, control)
            result = json.loads(stdout)

            # then
            self.assertIn('control', result[0])
            self.assertIn('foo', result[0]['control'])
            self.assertEqual(result[0]['control']['foo'], 'bar')
            self.assertEqual(stderr, 'Warning: "control" property overwritten')

    def test_pretty_print(self):

        with TempFile() as tmp:

            # given
            tmp.write('{"foo":"bar"}')

            echo = ['echo', '[{"files":"filename"}]']
            control = ['control.py', tmp.name()]

            # when
            output = self.pipe(echo, control)

            # then
            expected = json.dumps(json.loads(output), indent=4)
            self.assertEqual(output, expected)

    def test_retain_file_order(self):

        temp_files = []

        try:
            # given
            for i in xrange(3):
                temp_file = TempFile()
                temp_file.write('{"index":%d}' % i)
                temp_files.append(temp_file)

            capitals = [
                {'Hungary' : 'Budapest'},
                {'Spain' : 'Madrid'},
                {'Italy' : 'Rome'}
            ]

            echo = ['echo', str(capitals).replace("'", '"')]
            control = ['control.py'] + [x.name() for x in temp_files]

            # when
            result = json.loads(self.pipe(echo, control))

            # then
            for i, pair in enumerate(capitals):

                country = pair.keys()[0]
                capital = pair[country]

                self.assertIn(country, result[i])
                self.assertEqual(result[i][country], capital)
                self.assertEqual(result[i]['control']['index'], i)

        finally:
            for temp_file in temp_files:
                temp_file.delete()

    def test_omit_iterations(self):

        with TempFile() as tmp:

            # given
            tmp.write('{"foo":"bar"}')

            echo = ['echo', '[{"files":"a"}, {"files":"b"}]']
            control = ['control.py', '-', tmp.name()]

            # when
            stdout, stderr = self.pipe_with_stderr(echo, control)
            result = json.loads(stdout)

            # then
            self.assertEqual(stderr, 'Warning: control wells for iteration #1 not provided')
            self.assertFalse('control' in result[0])
            self.assertTrue('control' in result[1])


class TestNegative(ScriptTestCase):

    def test_no_stdin_nor_args(self):
        self.assertEqual(
            self.execute(['control.py']),
            'usage: (...) | control.py filename [filename ...]')

    def test_args_but_no_stdin(self):
        self.assertEqual(
            self.execute(['control.py', 'some', 'arg']),
            'usage: (...) | control.py filename [filename ...]')

    def test_stdin_but_no_args(self):
        self.assertEqual(
            self.pipe(['echo', '[{},{},{}]'], ['control.py']),
            'JSON array has 3 items but 0 argument(s) provided')

    def test_too_few_filenames(self):
        self.assertEqual(
            self.pipe(['echo', '[{},{},{}]'], ['control.py', 'some_filename']),
            'JSON array has 3 items but 1 argument(s) provided')

    def test_too_many_filenames(self):
        self.assertEqual(
            self.pipe(['echo', '[{},{},{}]'], ['control.py', 'a', 'b', 'c', 'd']),
            'JSON array has 3 items but 4 argument(s) provided')

    def test_files_dont_exist(self):
        self.assertIn(
            u"Error: [Errno 2] No such file or directory: u'a'",
            self.pipe_with_stderr(['echo', '[{},{},{}]'], ['control.py', 'a', 'b', 'c'])[1])


if __name__ == '__main__':
    unittest.main()
