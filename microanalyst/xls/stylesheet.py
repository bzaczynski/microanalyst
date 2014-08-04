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
# FITNESS FOR A PARTICULAR PURPOSE ANfD NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Minimalist syntax for XF records inspired by Cascading Style Sheets (CSS).

Supported properties:
* background-color
* border-color
* color
* font-weight
* text-align
* number-format (non-standard)

Supported selectors:
* wildcard "*"
* class selector, e.g. ".header"
* combined selectors, e.g. ".header, .footer"

Styles can be commented out.

XF records are cached due to the upper limit of 4k in a single xls file.

Sample usage:
>>> from microanalyst.xls import stylesheet
>>> style = stylesheet.load('colorful.css')
>>> for i in range(5):
>>>     xf = style('.header.big', alt=i % 2)
"""

import re
import xlwt


def load(filename):
    """Return Stylesheet object loaded from a file."""
    with open(filename) as file_handle:
        return parse(file_handle.read())


def parse(text):
    """Return Stylesheet object parsed from a string."""
    return Stylesheet(_parse(text))


class Stylesheet(object):
    """Factory of XF records built from a CSS-like syntax."""

    def __init__(self, styles):
        """@param styles: a dict of selectors and style declarations"""
        self._styles = styles
        self._cache = {}

    def __str__(self):
        return str(self._styles)

    def __call__(self, selector, **kwargs):
        """Return XF record for the given selectors."""
        return self._get_xf_record(self._synthesize(selector, **kwargs))

    def peek(self, selector):
        """Return style declarations for the given selector."""
        return self._styles[selector]

    def override(self, stylesheet):
        """Make an in-place union with another Stylesheet object."""
        self._styles = dict(self._styles, **stylesheet._styles)
        self._cache = dict(self._cache, **stylesheet._cache)

    def inline(self, text):
        """Return XF record for selector-less style declarations."""
        return self._get_xf_record(_parse('.inline {%s}' % text)['.inline'])

    def _get_xf_record(self, declarations):
        """Return cached XF record for the given style declarations."""

        key = self._get_digest(declarations)

        if not key in self._cache:
            self._cache[key] = _make_record(declarations)

        return self._cache[key]

    def _synthesize(self, selector, **kwargs):
        """Merge style declarations of given selectors."""

        class_names = {'.' + x for x in selector.split('.') if x}

        if kwargs:
            for class_name in kwargs:
                if kwargs[class_name]:
                    class_names.add('.' + class_name)

        declarations = {}
        for class_name in class_names:
            declarations.update(self._styles[class_name])

        return declarations

    @staticmethod
    def _get_digest(declarations):
        """Calculate digest of a combination of style declarations."""

        seed = []
        for property_name in sorted(declarations):
            seed.append(property_name)
            seed.append(declarations[property_name])

        return hash(''.join(seed))


def _parse(text):
    """Return a dict: { selector --> { property: value } }."""

    # remove comments between /* and */ (including nested ones)
    text = re.sub(r'/\*.*\*/', '', text, flags=re.DOTALL)

    # replace runs of consecutive whitespace with a single space
    text = re.sub(r'\s+', ' ', text)

    styles = {}

    tokens = re.split(r'{([^}]*)}', text)
    for selectors, block in zip(_trim(tokens[::2]), _trim(tokens[1::2])):

        declarations = [x for x in block.split(';') if x]
        declarations = dict([_trim(x.split(':')) for x in declarations])

        for selector in _trim(selectors.split(',')):

            assert re.match(r'^(\*|\.\w+)?$', selector), \
                   'invalid selector "%s"' % selector

            if selector in styles:
                styles[selector].update(declarations)
            else:
                styles[selector] = declarations.copy()

    # append wildcard declarations to all other styles
    if '*' in styles:
        wildcard = styles['*']
        for selector in styles:
            if selector != '*':
                styles[selector].update(wildcard)

    return styles


def _trim(strings):
    """Remove leading and trailing whitespace from each string."""
    return [x.strip() for x in strings]


def _make_record(declarations):
    """Translate CSS-like properties and values to a new XF record."""

    xf_styles = []

    font_style = None
    number_format = None

    for property_name, value in declarations.iteritems():

        if property_name == 'text-align':
            xf_styles.append('align: horizontal %s' % value)
        elif property_name == 'background-color':
            xf_styles.append('pattern: pattern solid, fore_color %s' % value)
        elif property_name == 'number-format':
            number_format = value
        elif property_name == 'border-color':
            sides = ['left', 'right', 'top', 'bottom']
            sizes = ['%s thin' % x for x in sides]
            colors = ['%s_color %s' % (x, value) for x in sides]
            xf_styles.append('border: ' + ', '.join(sizes + colors))
        elif property_name == 'color':
            if not font_style:
                font_style = 'font: color %s' % value
            else:
                font_style += ', color %s' % value
        elif property_name == 'font-weight':
            if not font_style:
                font_style = 'font: %s True' % value
            else:
                font_style += ', %s True' % value

    if font_style:
        xf_styles.append(font_style)

    return xlwt.easyxf('; '.join(xf_styles), num_format_str=number_format)
