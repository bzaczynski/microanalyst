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

from microanalyst.model.expression import Expression


class TestCompilation(unittest.TestCase):

    def test_expression_to_string(self):
        expr_str = 'foobar'
        expr_obj = Expression(expr_str)
        self.assertEqual(str(expr_obj), expr_str)

    def test_invalid_python_identifier(self):
        with self.assertRaises(SyntaxError):
            Expression('1x + 1')


class TestEvaluation(unittest.TestCase):

    def test_parameterless(self):
        pi = Expression('3.14159265359')
        self.assertAlmostEqual(pi(), 3.14159265359, delta=11)

    def test_single_parameter(self):
        is_even = Expression('x % 2 == 0')
        for value in xrange(100):
            self.assertEqual(is_even(value), value % 2 == 0)

    def test_single_parameter_repeated(self):
        polynomial = Expression('-x**2 + 2*x + 3')
        self.assertEqual(polynomial(0), 3)

    def test_multiple_parameters(self):
        add = Expression('a + b + c')
        self.assertEqual(add(1, 2, 3), 6)

    def test_default_parameter_order(self):
        projection = Expression('(x/z, y/z)')
        x, y = projection(10, 25, 5)
        self.assertTrue(x == y == 0)

    def test_explicit_parameter_order(self):
        projection = Expression('(x/z, y/z)', params=('x', 'y', 'z'))
        x, y = projection(10, 25, 5)
        self.assertEqual(x, 2)
        self.assertEqual(y, 5)

    def test_compound_parameter(self):
        age = Expression('now - person["birthdate"]', params=('person', 'now'))
        person = {'name': 'John', 'birthdate': 1973}
        self.assertEqual(age(person, 1999), 26)

    def test_builtins(self):
        average = Expression('sum(x) / float(len(x))')
        self.assertAlmostEqual(average([1, 2, 4]), 2.333, delta=3)

    def test_missing_scope(self):
        is_odd = Expression('not is_even(x)')
        with self.assertRaises(Exception):
            is_odd(3)

    def test_local_scope(self):
        is_even = Expression('x % 2 == 0')
        is_odd = Expression('not is_even(x)', locals())
        for value in xrange(100):
            self.assertEqual(is_odd(value), value % 2 != 0)

    def test_invalid_argument_type(self):
        add = Expression('a + b')
        with self.assertRaises(Exception):
            add('text', 123)

    def test_too_few_arguments(self):
        add = Expression('a + b')
        with self.assertRaises(Exception):
            add(0)

    def test_too_many_arguments(self):
        add = Expression('a + b')
        with self.assertRaises(Exception):
            add(1, 2, 3, 4, 5)

    def test_recursion(self):
        global factorial
        factorial = Expression('1 if x < 2 else x*factorial(x - 1)',
                               globals(),
                               ('x',))
        self.assertEqual(factorial(6), 720)


if __name__ == '__main__':
    unittest.main()
