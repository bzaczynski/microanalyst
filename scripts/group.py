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
Group files into annotated clusters and print the result as a JSON array.

Sample usage:
C:\\> group.py chapters\*.md --name "The Book" --edition 3
[
    {
        "files": [
            "chapters\\\\chapter1.md",
            "chapters\\\\chapter2.md",
            "chapters\\\\intro.md"
        ],
        "name": "The Book",
        "edition": 3
    }
]

Paths are always relative to the current directory.

Cluster annotations are optional. They can take arbitrary names except
for "files" which is ignored to avoid shadowing of the reserved key.
Annotations must be prefixed with at least one dash character "-" and
be followed by a space and a value. If specified annotations must be
places after filenames.

Pipes allow for concatenation of multiple clusters, e.g.
$ group.py folder1/* | group.py folder2/*
[
    {
        "files": [
            "folder1/a",
            "folder1/b",
            "folder1/c"
        ]
    },
    {
        "files": [
            "folder2/a",
            "folder2/b",
            "folder2/c"
        ]
    }
]
"""

import sys
import json
import argparse

from microanalyst.commons import osutils, uniutils


def parse(args):

    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', metavar='filename', type=str, nargs='+')

    known_args, unknown_args = parser.parse_known_args(args)

    return (
        uniutils.argv(known_args.filenames),
        uniutils.argv(unknown_args)
    )


def cast(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def list2dict(sequence):
    keys = [x.strip(u'-') for x in sequence[::2]]
    values = [cast(x) for x in sequence[1::2]]
    return dict(zip(keys, values))


def make_cluster(filenames, annotations):
    cluster = list2dict(annotations)
    cluster[u'files'] = osutils.expand(filenames)
    return cluster


def main(args):

    array = [make_cluster(*parse(args))]

    if not sys.stdin.isatty():
        pipe = json.loads(u''.join(uniutils.stdin()))
        array = pipe + array

    print json.dumps(array, indent=4)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print >> sys.stderr, 'Aborted'
