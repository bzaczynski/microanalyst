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
Lambda function built dynamically from string.
"""

import re
import keyword
import collections


class Expression(object):
    """Python's anonymous function wrapper.

    Example:
    >>> from microanalyst.model.expression import Expression
    >>> is_even = Expression('x % 2 == 0')
    >>> print is_even
    x % 2 == 0
    >>> print is_even(2)
    True

    The optional "scope" allows to evaluate custom variables:
    >>> scope = {'is_even': is_even}
    >>> is_odd = Expression('not is_even(x)', scope)
    >>> print is_odd(3)
    True

    Use locals() to refer to variables in the current scope:
    >>> is_even = Expression('x % 2 == 0')
    >>> is_odd = Expression('not is_even(x)', locals())

    Use globals() and forward declarations for recursive calls:
    >>> expr = '1 if n < 2 else fib(n - 2) + fib(n - 1)'
    >>> global fib
    >>> fib = Expression(expr, globals(), ('n',))
    >>> print fib(11)
    144

    Enforce parameter order with explicit "params":
    >>> pp = Expression('(x/z, y/z)', params=('x', 'y', 'z'))
    >>> x, y = pp(10, 25, 5)
    """

    def __init__(self, expr, scope=None, params=None):
        """Compile a lambda expression.

        Parameters:
        expr: str, lambda body
        scope: dict, variable names and their values (optional)
        params: tuple or list, ordered parameter names (optional)
        """
        self.expr = expr
        self.func = eval(_parse(expr, scope, params), scope)

    def __str__(self):
        return self.expr

    def __call__(self, *args):
        return self.func(*args)


def _parse(expr, scope, params):
    """Return string representation of a lambda function."""

    if not params:
        params = _extract_variables(expr, scope)

    return 'lambda %s: %s' % (','.join(params), expr)


def _extract_variables(expr, scope):
    """Return an ordered list of expression variables."""

    variables = collections.OrderedDict()

    reserved = globals()['__builtins__']
    pattern = re.compile(r'\b[_a-z][_a-z0-9]*', re.IGNORECASE)
    for item in pattern.findall(expr):
        if not keyword.iskeyword(item):
            if not item in reserved:
                if not (scope and item in scope):
                    variables[item] = None

    return variables.keys()
