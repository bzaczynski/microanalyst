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

from microanalyst.model import thresholds


class TestThresholds(unittest.TestCase):

    def test_default_threshold_values(self):

        # given
        t = thresholds.Thresholds()

        # then
        self.assertEqual(str(t.starvation()), 'x <= 0.2')
        self.assertEqual(str(t.infection()), 'x >= 0.8')
        self.assertEqual(str(t.violation()), 'x > 0.06')

    def test_reset_to_default(self):

        # given
        t = thresholds.Thresholds()
        t.starvation('foo')
        t.infection('bar')
        t.violation('baz')

        # when
        t.set_default()

        # then
        self.assertEqual(str(t.starvation()), 'x <= 0.2')
        self.assertEqual(str(t.infection()), 'x >= 0.8')
        self.assertEqual(str(t.violation()), 'x > 0.06')

    def test_callable(self):

        # given
        t = thresholds.Thresholds()

        # then
        self.assertTrue(t.starvation()(0.2))
        self.assertTrue(t.infection()(0.8))
        self.assertFalse(t.violation()(0.06))

    def test_setters(self):

        # given
        t = thresholds.Thresholds()

        # when
        t.starvation('foo')
        t.infection('bar')
        t.violation('baz')

        # then
        self.assertEqual(str(t.starvation()), 'foo')
        self.assertEqual(str(t.infection()), 'bar')
        self.assertEqual(str(t.violation()), 'baz')


if __name__ == '__main__':
    unittest.main()
