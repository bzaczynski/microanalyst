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
Read Microsoft(R) Excel(TM) spreadsheet files containing microplate
measurements obtained with Tecan(R) i-control(TM) software, assemble
their contents and print the result in JSON format.

Sample usage:
C:\\> echo [{"files":["data1.xls","data2.xls"]}] | assemble.py

Input can also be supplied via stdin and terminated with an EOF (Ctrl+D):
$ ./assemble.py
[
    {
        "files": [
            "data1.xls",
            "data2.xls"
        ]
    }
]
EOF

There is a helper script distributed as part of this software,
which allows for a much more convenient workflow, though:
C:\\> group.py series1/*xls | group.py series2/*xls | assemble.py

The expected input is a JSON array of one or more objects corresponding to
clusters/iterations (experiment iterations). Each such object has a mandatory
"files" array with pathnames to Microsoft(R) Excel(TM) spreadsheet files.
In addition to the "files" attribute clusters are free to define custom
annotations which are retained in the final result.

Non-ASCII characters within JSON attributes and values including filenames
should be escaped with Unicode NFC escape sequences.

Path separator is platform dependent, thus, both a slash "/" and double
backslash "\\\\" are accepted for pathnames.

Excerpt from a sample result:
{
    "iterations": [
        {
            "spreadsheets": [
                {
                    "filename": "ex2\\seria1\\GAL_s01_21dni.xls",
                    "microplates": {
                        "001": {
                            "temperature": 23.6,
                            "timestamp": "2014-01-13T12:43:19",
                            "values": [
                                0.7384999990463257,
                                0.7184000015258789,
                                (...)
                            ]
                        },
                        (...)
                    }
                },
                (...)
            ]
        }
    ]
}
"""

import os
import re
import sys
import json
import time
import datetime
import xlrd

from microanalyst.commons import uniutils


def is_valid(sheet):
    """Check if worksheet conforms to Tecan(R) i-control(TM) format."""
    if sheet.nrows >= 36 and sheet.ncols >= 13:
        signature = 'Application: Tecan i-control'
        return sheet.cell_value(0, 0) == signature


def parse_datetime(text):
    """Return date and time according to ISO 8601 standard."""
    tm_struct = time.strptime(text, '%Y-%m-%d %H:%M:%S')
    iso8601 = datetime.datetime(*tm_struct[0:6]).isoformat()
    return uniutils.str2unicode(iso8601)


def parse_temperature(text):
    """Return temperature in Celsius degrees."""
    match = re.search(ur'\s([^\s]+)\s', text)
    return float(match.group(1)) if match else None


def get_well_values(sheet):
    """Return a list of well values in row-major order."""

    values = []
    for row in xrange(24, 32):
        for col in xrange(1, 13):
            values.append(float(sheet.cell_value(row, col)))

    return values


def get_microplates(filename):
    """Return microplates and their values for a given filename."""

    microplates = {}

    workbook = xlrd.open_workbook(filename)
    for sheet in workbook.sheets():
        if is_valid(sheet):
            microplates[sheet.name] = {
                u'timestamp': parse_datetime(sheet.cell_value(20, 1)),
                u'temperature': parse_temperature(sheet.cell_value(22, 1)),
                u'values': get_well_values(sheet)
            }

    return microplates


def date2str(iso8601):
    """Return only the date portion of an ISO 8601 datetime."""
    match = re.search(ur'([^T]+)T', iso8601)
    return match.group(1) if match else None


def earliest(microplates):
    """Return the earliest timestamp of the microplates in a single file."""
    timestamps = [date2str(microplates[x][u'timestamp']) for x in microplates]
    timestamps.sort()
    return timestamps[0]


def main():

    json_data = json.loads(u''.join(uniutils.stdin()))

    for iteration in json_data:

        files = iteration[u'files']
        for i, filename in enumerate(files):
            files[i] = {
                u'filename': os.path.abspath(filename),
                u'microplates': get_microplates(filename)
            }

        # ISO 8601 dates can be sorted lexicographically
        files.sort(key = lambda x: earliest(x[u'microplates']))

        # rename "files" to "spreadsheets"
        iteration[u'spreadsheets'] = iteration.pop(u'files')

    print json.dumps({'iterations': json_data},
                     indent=4,
                     sort_keys=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print >> sys.stderr, 'Aborted'
