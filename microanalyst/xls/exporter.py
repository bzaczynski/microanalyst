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
Skeleton for scripts exporting JSON data to Microsoft(R) Excel(TM).
"""

import os
import sys
import argparse
import json

import xlwt

from microanalyst.model import Model
from microanalyst.commons import osutils, uniutils


class Exporter(object):
    """Common logic for the export scripts."""

    def __init__(self, TemplateClass):

        if sys.stdin.isatty():
            usage = 'usage: (...) | %s <file.xls> [-f] [--binary]' \
                    ' [--colors] [--stylesheet <file.css>]'
            print usage % os.path.basename(sys.argv[0])
        else:

            params = _parse(sys.argv[1:])

            if not _can_write(params):
                print 'File already exists. Use the -f flag to force overwrite.'
            else:

                workbook = xlwt.Workbook()

                print '[1/3] Processing...',
                model = Model(json.loads(u''.join(uniutils.stdin())))
                print 'done'

                template = TemplateClass(
                    model,
                    params.stylesheet,
                    params.colors,
                    params.binary)

                print '[2/3] Rendering...',
                template.render(workbook)
                print 'done'

                print '[3/3] Saving...',
                workbook.save(params.filename)
                print 'done'

                osutils.open_with_default_app(params.filename)


def _parse(args):
    """<file.xls> [-f] [--binary] [--colors] [--stylesheet <file.css>]"""

    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-f', '--force-overwrite', action='store_true')
    parser.add_argument('--stylesheet', metavar='style.css')
    parser.add_argument('--colors', action='store_true', default=False)
    parser.add_argument('--binary', action='store_true', default=False)

    return parser.parse_args(args)


def _can_write(params):
    """Check if file exists and if the -f flag is defined."""

    if os.path.exists(params.filename):
        return params.force_overwrite

    return True
