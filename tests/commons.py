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

import unittest
import platform
import subprocess

from subprocess import Popen
from microanalyst.commons import uniutils


class ScriptTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.encoding = uniutils.SysEncoding()
        cls.use_shell = platform.system() == 'Windows'

    def execute(self, command, **kwargs):
        return normalize(subprocess.check_output(command, shell=self.use_shell, **kwargs))

    def pipe(self, *args):

        processes = []
        last_process = None

        for arg in args:

            if last_process:
                process = Popen(arg, shell=self.use_shell,
                                stdin=last_process.stdout,
                                stdout=subprocess.PIPE)
            else:
                process = Popen(arg, shell=self.use_shell,
                                stdout=subprocess.PIPE)

            last_process = process
            processes.append(process)

        return normalize(processes[-1].communicate()[0])

    def pipe_with_stderr(self, *args):

        processes = []
        last_process = None

        for arg in args:

            if last_process:
                process = Popen(arg, shell=self.use_shell,
                                stdin=last_process.stdout,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            else:
                process = Popen(arg, shell=self.use_shell,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

            last_process = process
            processes.append(process)

        stdout, stderr= processes[-1].communicate()
        return (normalize(stdout), normalize(stderr))

    def skip_due_to_encoding(self, encoding):
        self.skipTest("Unicode cannot be represented with platform's charset: %s" % encoding)


def normalize(text):
    return text.replace('\r', '').strip()
