#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2013, 2014 Bartosz Zaczynski
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
Check if Python source files use Unix-style newline character.

Otherwise running the scripts on Linux will end up with this error:
: No such file or directory
"""

import os

from os.path import abspath, join


def get_python_source_files():

    self = __file__.replace('\\', '/')
    for root, folders, files in os.walk(r'.'):

        if '.git' in root or 'build' in root:
            continue

        for file_name in files:

            file_name = abspath(join(root, file_name)).replace('\\', '/')

            if file_name == self:
                continue

            if file_name.endswith(('.py', '.pyw')):
                yield file_name


def get_broken_files():

    broken_files = {}

    for file_name in get_python_source_files():

        with open(file_name, 'U') as file_handle:

            file_handle.read()

            if file_handle.newlines is not None:

                def make_list(obj):
                    if isinstance(obj, str):
                        return [obj]
                    else:
                        return list(obj)

                newlines = make_list(file_handle.newlines)

                if '\r' in newlines or '\r\n' in newlines:
                    broken_files[file_name] = newlines

    return broken_files


def main():

    broken_files = get_broken_files()

    if len(broken_files) > 0:
        print r'The following files contain invalid newline characters:'
        for i, file_name in enumerate(sorted(broken_files)):
            newlines = ', '.join([repr(x) for x in broken_files[file_name]])
            print '%2d. %s (%s)' % (i + 1, file_name, newlines)
    else:
        print 'Ready to commit!'


if __name__ == '__main__':
    main()
