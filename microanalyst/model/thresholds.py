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
A set of boolean conditions for microplate's well evaluation.

To get an existing condition:
>>> thresholds = Thresholds()
>>> print thresholds.starvation()
x <= 0.2

To set a new condition:
>>> thresholds.starvation('x < 0.5')

To use a condition:
>>> is_starved = thresholds.starvation()
>>> is_starved(0.5)
False
"""

from microanalyst.model.expression import Expression


class Thresholds(object):
    """Boolean conditions for starvation, infection and control violation."""

    def __init__(self):
        self.set_default()

    def set_default(self):
        """Set default thresholds."""
        self._starvation = Expression('x <= 0.2')
        self._infection = Expression('x >= 0.8')
        self._violation = Expression('x > 0.06')

    def starvation(self, expr=None):
        """Starvation threshold getter/setter."""
        if expr:
            self._starvation = Expression(expr)
        else:
            return self._starvation

    def infection(self, expr=None):
        """Infection threshold getter/setter."""
        if expr:
            self._infection = Expression(expr)
        else:
            return self._infection

    def violation(self, expr=None):
        """Control violation threshold getter/setter."""
        if expr:
            self._violation = Expression(expr)
        else:
            return self._violation


def default():
    """Return a tuple with default threshold expressions.

    >>> from microanalyst.model import thresholds
    >>> is_starved, is_infected, is_violated = thresholds.default
    """
    instance = Thresholds()
    return (instance.starvation(),
            instance.infection(),
            instance.violation())