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
Append "genes" property to a JSON dictionary.
"""

import sys
import json

from microanalyst.commons import osutils, uniutils


def parse(args):
    return osutils.expand(uniutils.argv(args))[0]


def load_json(filename):
    with open(filename, 'r') as file_handle:
        return json.load(file_handle)


def main(args):

    if sys.stdin.isatty():
        print 'usage: (...) | genes.py filename'
    else:
        json_data = json.loads(u''.join(uniutils.stdin()))

        if type(json_data) is dict:
            json_data[u'genes'] = load_json(parse(args))
            print json.dumps(json_data, indent=4, sort_keys=True)
        else:
            print >> sys.stderr, 'The root element of JSON input must be an object but got: %s' % type(json_data)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print >> sys.stderr, 'Aborted'
