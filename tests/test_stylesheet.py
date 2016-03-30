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

from microanalyst.xls import stylesheet


class TestCommentParser(unittest.TestCase):

    def test_truncate_comments_one_line(self):
        css = '.selector { property: /* one line comment */ value }'
        expected = "{'.selector': {'property': 'value'}}"
        self.assertEqual(str(stylesheet.parse(css)), expected)

    def test_truncate_comments_multiple_lines(self):
        css = '.selector { property: /* multiple\nlines\ncomment */ value }'
        expected = "{'.selector': {'property': 'value'}}"
        self.assertEqual(str(stylesheet.parse(css)), expected)

    def test_truncate_comments_tricky(self):
        css = '.selector { property:/*/ <-- tricky */ value }'
        expected = "{'.selector': {'property': 'value'}}"
        self.assertEqual(str(stylesheet.parse(css)), expected)

    def test_truncate_comments_nested_one_line(self):
        css = '.selector { property:/* nested /* comment */ one line */ value }'
        expected = "{'.selector': {'property': 'value'}}"
        self.assertEqual(str(stylesheet.parse(css)), expected)

    def test_truncate_comments_nested_multiple_lines(self):
        css = '.selector { property:/* nested\n/*comment\nspanning\nmultiple */\nlines */ value }'
        expected = "{'.selector': {'property': 'value'}}"
        self.assertEqual(str(stylesheet.parse(css)), expected)


class TestSelectorParser(unittest.TestCase):

    def test_intersection_selectors(self):
        css = '.foo.bar {}'
        with self.assertRaises(AssertionError):
            stylesheet.parse(css)

    def test_compound_selector(self):
        css = '.foo .bar {}'
        with self.assertRaises(AssertionError):
            stylesheet.parse(css)

    def test_combined_selectors(self):
        css = stylesheet.parse('.foo, .bar {}')
        self.assertIn('.foo', css._styles)
        self.assertIn('.bar', css._styles)


class TestPropertyParser(unittest.TestCase):

    def test_empty_style(self):
        css = '.selector {}'
        expected = "{'.selector': {}}"
        self.assertEqual(str(stylesheet.parse(css)), expected)

    def test_single_style_no_semicolon(self):
        css = '.selector { font-weight: normal }'
        expected = "{'.selector': {'font-weight': 'normal'}}"
        self.assertEqual(str(stylesheet.parse(css)), expected)

    def test_single_style_with_semicolon(self):
        css = '.selector { font-weight: normal; }'
        expected = "{'.selector': {'font-weight': 'normal'}}"
        self.assertEqual(str(stylesheet.parse(css)), expected)

    def test_multiple_styles_no_semicolon_at_the_end(self):

        css = '.selector { font-weight: normal; font-face: Arial }'

        actual = stylesheet.parse(css)
        block = actual._styles['.selector']

        self.assertTrue('font-weight' in block)
        self.assertTrue('font-face' in block)

        self.assertEqual(block['font-weight'], 'normal')
        self.assertEqual(block['font-face'], 'Arial')

    def test_merge_duplicate_selectors(self):

        css = stylesheet.parse('''
            .s1 {
                font-weight: bold;
            }

            .s2 {
                text-align: center;
            }

            .s1 {
                color: red;
            }
        ''')

        actual = css._styles

        self.assertIn('font-weight', actual['.s1'])
        self.assertIn('color', actual['.s1'])

    def test_combined_selectors(self):

        css = stylesheet.parse('''
            .h1, .h2 {
                color: red;
            }

            .h3 {
                font-weight: bold;
            }

            .h1 {
                text-align: right;
            }
        ''')

        actual = css._styles

        self.assertTrue(len(actual['.h1']), 2)
        self.assertIn('color', actual['.h1'])
        self.assertIn('text-align', actual['.h1'])

        self.assertTrue(len(actual['.h2']), 1)
        self.assertIn('color', actual['.h2'])

        self.assertTrue(len(actual['.h3']), 1)
        self.assertIn('font-weight', actual['.h3'])


class TestCache(unittest.TestCase):

    def setUp(self):
        self.css = stylesheet.parse('.big { font-size: 32pt } .blue { color: blue }')
        self.css_dup = stylesheet.parse('.foo { color: red } .bar { color: red }')

    def test_cache_same_style_different_order(self):

        # when
        xf_1 = self.css('.big.blue')
        xf_2 = self.css('.blue.big')

        # then
        self.assertEqual(xf_1, xf_2)

    def test_cache_same_style_different_names(self):

        # when
        xf_1 = self.css_dup('.foo')
        xf_2 = self.css_dup('.bar')

        # then
        self.assertEqual(xf_1, xf_2)

    def test_cache_duplicate_styles(self):

        # when
        xf_1 = self.css_dup('.foo.bar')
        xf_2 = self.css_dup('.bar.foo')

        # then
        self.assertEqual(xf_1, xf_2)

    def test_cache_alternative_syntax(self):

        css = stylesheet.parse('''
            .header {
                font-weight: bold;
            }

            .binary {
                number-format: 0;
                text-align: center;
            }

            .alt {
                background-color: gray25;
            }
        ''')

        xf_1 = css('.header.binary.alt')
        xf_2 = css('.header.binary', alt=True)
        xf_3 = css('.header', alt=True, binary=True)

        self.assertEqual(xf_1, xf_2)
        self.assertEqual(xf_2, xf_3)

    def test_exclude_false_property(self):

        css = stylesheet.parse('''
            .header {
                font-weight: bold;
            }

            .alt {
                background-color: gray25;
            }
        ''')

        xf_1 = css('.header', alt=True)
        xf_2 = css('.header', alt=False)

        self.assertNotEqual(xf_1, xf_2)

    def test_dont_cache_unique_styles(self):

        # given
        css = stylesheet.parse('.big { font-size: 32pt } .blue { color: blue }')

        # when
        xf_1 = css('.big')
        xf_2 = css('.blue')

        # then
        self.assertNotEqual(xf_1, xf_2)

    def test_cache_inline_styles(self):

        # given
        css = stylesheet.parse('.center { text-align: center }')

        # when
        xf = css.inline('text-align: center')

        # then
        self.assertEqual(xf, css('.center'))


class TestOverride(unittest.TestCase):

    def setUp(self):

        self.css1 = stylesheet.parse('''
            .s1 {
                text-align: center;
                color:red;
            }

            .s2 {
                number-format: 0
            }
        ''')

        self.css2 = stylesheet.parse('''
            .s1 {
                font-weight: bold;
            }

            .s3 {
                background-color: gray25;
            }
        ''')

    def test_retain_non_overlapping_selectors(self):

        # when
        self.css1.override(self.css2)

        # then
        self.assertEqual(self.css1._styles['.s2'], {'number-format': '0'})
        self.assertEqual(self.css1._styles['.s3'], {'background-color': 'gray25'})

    def test_override_overlapping_selectors(self):

        # when
        self.css1.override(self.css2)

        # then
        self.assertEqual(self.css1._styles['.s1'], {'font-weight': 'bold'})

    def test_non_commutative(self):

        # when
        self.css2.override(self.css1)

        # then
        self.assertEqual(self.css2._styles['.s1'], {
            'text-align': 'center',
            'color': 'red'
        })

    def test_merge_cache(self):

        # given
        xf2 = self.css1('.s2')
        xf3 = self.css2('.s3')

        # when
        self.css1.override(self.css2)

        # then
        self.assertEqual(xf2, self.css1('.s2'))
        self.assertEqual(xf3, self.css1('.s3'))


class TestWildcard(unittest.TestCase):

    def setUp(self):
        self.css = css = stylesheet.parse('''
            * {
                font-weight: bold;
            }

            .s1 {
                border-color: blue;
            }

            .s2 {
                text-align: center;
            }

            * {
                color: red;
            }
        ''')

    def test_merge_duplicate_wildcards(self):

        actual = self.css._styles

        self.assertIn('font-weight', actual['*'])
        self.assertIn('color', actual['*'])

    def test_apply_wildcard_to_all(self):

        actual = self.css._styles

        self.assertIn('border-color', actual['.s1'])
        self.assertIn('font-weight', actual['.s1'])
        self.assertIn('color', actual['.s1'])

        self.assertIn('text-align', actual['.s2'])
        self.assertIn('font-weight', actual['.s2'])
        self.assertIn('color', actual['.s2'])

    def test_combined_styles_with_wildcard(self):

        css = stylesheet.parse('''
            .s1, *, .s2 {
                font-weight: bold;
            }

            .s3 {
                text-align: center;
            }
        ''')

        actual = css._styles

        self.assertIn('font-weight', actual['.s1'])
        self.assertIn('font-weight', actual['.s2'])
        self.assertIn('font-weight', actual['.s3'])
        self.assertIn('text-align', actual['.s3'])


if __name__ == '__main__':
    unittest.main()
