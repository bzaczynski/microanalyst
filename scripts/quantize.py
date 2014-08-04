#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2013 Bartosz Zaczynski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Read experiment data in JSON format produced by the assemble.py script,
apply quantization algorithm to all microplate values and print output
retaining all extra information such as gene names and control wells.

Default quantized values:
 2 - control well (violated or not), including extra control wells
 1 - other (including neutral and infected)
 0 - starved

Sample usage:
$ ... | quantize.py --starved 0 --control 1 --other 1
"""

import sys
import json
import argparse
import numpy

import microanalyst.model

from microanalyst.model import thresholds
from microanalyst.commons import uniutils


def parse(args):
    """[--starved <int>] [--control <int>] [--other <int>]"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--control', metavar='level', type=int, default=2)
    parser.add_argument('--other', metavar='level', type=int, default=1)
    parser.add_argument('--starved', metavar='level', type=int, default=0)

    return parser.parse_args(args)


def quantize_control_wells(model, levels):
    """Replace control well values with a constant."""
    model.values()[model.control_mask.values] = levels.control


def quantize_non_control_wells(model, levels):
    """Replace values of wells other than controls with relevant constants."""

    levels = {
        True: levels.starved,
        False: levels.other
    }

    is_starved = thresholds.Thresholds().starvation()
    set_level = numpy.vectorize(lambda x: levels[is_starved(x)])

    model.values()[~model.control_mask.values] = set_level(
        model.values()[~model.control_mask.values]
    )


def update(json_data, model):
    """Update JSON with quantized values from the model."""
    for i, iteration in enumerate(json_data[u'iterations']):
        for j, spreadsheet in enumerate(iteration[u'spreadsheets']):
            for name, microplate in spreadsheet[u'microplates'].items():
                microplate[u'values'] = [int(x) for x in model.values(i, j, name)]


def main(args):

    if sys.stdin.isatty():
        print 'usage: (...) | assemble.py | quantize.py'
    else:

        json_data = json.loads(u''.join(uniutils.stdin()))
        levels = parse(args)

        model = microanalyst.model.Model(json_data)

        quantize_control_wells(model, levels)
        quantize_non_control_wells(model, levels)

        update(json_data, model)

        print json.dumps(json_data, indent=4, sort_keys=True)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print >> sys.stderr, 'Aborted'
