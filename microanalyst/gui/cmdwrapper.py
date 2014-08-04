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
Utilities for executing microanalyst scripts in a native terminal
such as cmd.exe or xterm according to platform-specific syntax
and shell commands.
"""

import os
import platform

from microanalyst.commons.osutils import TempFile


class ScriptWrapper(object):
    """Transforms metadata into shell command and executes it."""

    def __init__(self, iterations, filename, keep_json, genes):
        """
            iterations: [{'files':[''],'control':tk.StringVar()}]
            filename: str, output Excel(TM)
            keep_json: bool
        """

        self.iterations = iterations
        self.filename = filename
        self.keep_json = keep_json
        self.genes = genes

        self.shell = _get_shell()

    def xlsh(self):
        """Call xlsh.py for microplates in separate worksheets."""

        cmd_builder = self._get_builder()
        cmd_builder.xlsh()

        self._execute(cmd_builder)

    def xlsv(self):
        """Call xlsv.py for microplates in a single worksheet."""

        cmd_builder = self._get_builder()
        cmd_builder.xlsv()

        self._execute(cmd_builder)

    def _execute(self, cmd_builder):

        message = 'echo Please wait while processing... && '
        command = self.shell.template % (message + str(cmd_builder))
        os.system(command)

    def _get_builder(self):

        cmd_builder = CommandBuilder(self.shell,
                                     self.iterations,
                                     self.filename,
                                     self.genes)

        cmd_builder.group().control().assemble()

        if self.genes is not None:
            cmd_builder.genes()

        if self.keep_json:
            cmd_builder.redirect()

        return cmd_builder


class CommandBuilder(object):
    """Builder of a shell command according to platform-specific syntax."""

    def __init__(self, shell, iterations, filename, genes):
        self.shell = shell
        self.iterations = iterations
        self.filename = filename
        self.genes_def = genes
        self.command = []

    def __str__(self):
        return ' '.join(self.command)

    def group(self):
        """Generate group.py script invocation, e.g.
           $ group.py "file1" "file2" | group.py "file3" | ...
        """

        for iteration in self.iterations:
            self.command.append('group.py')
            for filename in iteration['files']:
                self.command.append(self.shell.quote(filename))
            self.command.append('|')

        return self

    def control(self):
        """Generate control.py script invocation, e.g.
           $ ... | control.py "file1" - "file3" | ...
        """

        control = ['control.py']
        for iteration in self.iterations:

            filename = iteration['control'].get()

            if filename:
                control.append(self.shell.quote(filename))
            else:
                control.append('-')

        self.command.extend(control)
        self.command.append('|')

        return self

    def assemble(self):
        """Generate assemble.py script invocation."""
        self.command.append('assemble.py')
        return self

    def genes(self):
        """Generate genes.py script invocation, e.g.
           $ ... | genes.py "file" | ...
        """

        tmp = TempFile()
        tmp.write(self.genes_def)

        self.command.append('|')
        self.command.append('genes.py')
        self.command.append(self.shell.quote(tmp.name()))

        return self

    def redirect(self):
        """Keep intermediate JSON by redirecting assemble.py to a file."""
        json_filename = self.shell.quote(self.filename[:-4] + '.json')
        self.command.append(r'> %s && %s %s' % (json_filename,
                                                self.shell.cat,
                                                json_filename))
        return self

    def xlsh(self):
        """Generate xlsh.py script invocation (horizontal layout)."""
        return self._xls_script('xlsh.py')

    def xlsv(self):
        """Generate xlsh.py script invocation (vertical layout)."""
        return self._xls_script('xlsv.py')

    def _xls_script(self, name):
        self.command.append('| ' + name)
        self.command.append(r'%s -f' % self.shell.quote(self.filename))
        return self


class WindowsShell(object):
    """Command templates for a Windows shell."""

    def __init__(self):
        self.template = r'start cmd /c "%s"'
        self.cat = 'type'

    def quote(self, filename):
        """Escape filename with Windows-style quotation marks."""
        return r'"%s"' % filename


class UnixShell(object):
    """Command templates for a Mac/Linux/Unix shell."""

    def __init__(self):
        self.template = r'xterm -e "%s && sleep 5s" &'
        self.cat = 'cat'

    def quote(self, filename):
        """Escape filename with Unix-style quotation marks."""
        return r'\"%s\"' % filename


def _get_shell():
    """Return shell templates for the current OS."""
    return WindowsShell() if _is_windows() else UnixShell()


def _is_windows():
    """Return true if the current OS is Windows, false otherwise."""
    return platform.system() == 'Windows'
