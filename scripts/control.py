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
Append "control" property to each item in a JSON array.

Sample usage:
$ echo [{},{},{}] | control.py filename1 filename2 filename3
[
    {
        "control": {
            (...)      <--- filename1 contents
        }
    },
    {
        "control": {
            (...)      <--- filename2 contents
        }
    },
    {
        "control": {
            (...)      <--- filename3 contents
        }
    }
]

The actual content put inside "control" properties is loaded from
JSON-formatted files given as program arguments. Their number and
order must match JSON array supplied via standard input.

The intended purpose of this script is to allow for definition of
control wells in a iterations/cluster. Control wells must conform to
the following format where dictionary keys are microplate names:
{
    "002": ["A4"],
    "006": ["A4", "D5", "E7", "F3", "G3", "G8", "H12"],
    "B001": ["H1", "H7"],
    "B002": ["G2", "H5", "H6", "H7", "H8", "H9", "H12"]
    (...)
}

Typical usage would look like this:
C:\\> group.py series1/*.xls | (...) | control.py series1/ctrl.json (...)

Use a dash character "-" to explicitly omit certain iterations, e.g.
C:\\> (...) | control.py - - series3/ctrl.json -
"""

import sys
import json

from microanalyst.commons import osutils, uniutils


def parse(args):
    return osutils.expand(uniutils.argv(args))


def load_json(filename):
    with open(filename, 'r') as file_handle:
        return json.load(file_handle)


def main(args):

    if sys.stdin.isatty():
        print 'usage: (...) | control.py filename [filename ...]'
    else:

        json_data = json.loads(u''.join(uniutils.stdin()))

        if len(json_data) != len(args):
            template = 'JSON array has %d items but %d argument(s) provided'
            print template % (len(json_data), len(args))
            sys.exit(1)

        for i, filename in enumerate(parse(args)):

            if filename == '-':
                message = 'Warning: control wells for iteration #%d not provided'
                print >> sys.stderr, message % (i + 1)
                continue

            if u'control' in json_data[i]:
                print >> sys.stderr, 'Warning: "control" property overwritten'

            json_data[i][u'control'] = load_json(filename)

        print json.dumps(json_data, indent=4, sort_keys=True)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print >> sys.stderr, 'Aborted'
