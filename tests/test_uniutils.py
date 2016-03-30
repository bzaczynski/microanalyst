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

from microanalyst.commons import uniutils


class TestSystemEncodings(unittest.TestCase):

    def test_has_all_system_encodings(self):
        encoding = uniutils.SysEncoding()
        self.assertTrue(hasattr(encoding, 'command_line'))
        self.assertTrue(hasattr(encoding, 'arguments'))
        self.assertTrue(hasattr(encoding, 'filenames'))

    def test_print_dict(self):
        self.assertIsInstance(eval(str(uniutils.SysEncoding())), dict)


class TestStringToUnicode(unittest.TestCase):

    def test_return_same_object_if_already_unicode(self):
        src = u'some Unicode string'
        dst = uniutils.str2unicode(src)
        self.assertEqual(id(src), id(dst))

    def test_decode_with_utf8_by_default(self):
        src = r'za\u017c\xf3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144'
        dst = uniutils.str2unicode(src).encode('utf-8')
        self.assertEqual(src, dst)

    def test_decode_with_custom_encoding(self):
        src = r'za\xbf\xf3\xb3\xe6 g\xea\xb6l\xb1 ja\xbc\xf1'
        dst = uniutils.str2unicode(src, 'iso8859-2').encode('iso8859-2')
        self.assertEqual(src, dst)


class TestEscapeUnicode(unittest.TestCase):

    def test_return_same_object_if_not_unicode(self):
        src = 'plain text'
        dst = uniutils.escape_unicode(src)
        self.assertEqual(id(src), id(dst))

    def test_convert_unicode_to_str(self):
        src = u'some Unicode string'
        self.assertIsInstance(uniutils.escape_unicode(src), str)

    def test_escape_unicode_characters(self):
        src = u'za\u017c\xf3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144'
        dst = r'za\u017c\xf3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144'
        self.assertEqual(uniutils.escape_unicode(src), dst)


if __name__ == '__main__':
    unittest.main()
