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
Streamlined interface to Tcl/Tk on top of Tkinter with more intuitive
and established names for widgets and their properties.
"""

import os
import re
import ttk
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import tkFont


class FileDialog(object):
    """Wrapped tkFileDialog with customized settings."""

    FILTER_ALL = ('All files', '.*')
    FILTER_XLS = ('Microsoft Excel', '.xls')
    FILTER_JSON = ('JSON', '.json')

    def save(self, cwd):
        """Open "save as" dialog with .xls file filter."""
        return _normalize(
                    tkFileDialog.asksaveasfilename(
                        initialdir=cwd,
                        filetypes=[self.FILTER_XLS],
                        defaultextension=self.FILTER_XLS[1]
                    )
                )

    def open_file(self, cwd, filters=None):
        """Browse for a file with arbitrary extension."""
        return _normalize(
                    tkFileDialog.askopenfilename(
                        initialdir=cwd,
                        filetypes=filters or [self.FILTER_ALL]
                    )
                )

    def open_files(self, cwd):
        """Browse for multiple .xls files"""
        return _normalize(
                    _fix_tkinter_bug(
                        tkFileDialog.askopenfilenames(
                            initialdir=cwd,
                            filetypes=[self.FILTER_XLS]
                        )
                    )
                )


def _normalize(obj):
    """Convert path(s) to platform's native format."""

    if obj:
        if isinstance(obj, (tuple, list)):
            return [os.path.normpath(item) for item in obj]
        else:
            return os.path.normpath(obj)

    return None


def _fix_tkinter_bug(filenames):
    """Convert Tcl list to Python list (necessary on Windows)."""

    if not isinstance(filenames, (tuple, list)):
        filenames = re.findall(r'{[^}]+}|\S+', filenames)
        filenames = [re.sub('^{|}$', '', i) for i in filenames]

    return filenames


class _Widget(object):
    """Mixin to be inherited from along with a Tkinter component."""

    def enable(self):
        self['state'] = tk.NORMAL

    def disable(self):
        self['state'] = tk.DISABLED

    def make_readonly(self):
        self['state'] = 'readonly'


class Label(ttk.Label, _Widget):

    def __init__(self, parent, **kwargs):
        ttk.Label.__init__(self, parent, **kwargs)

    @property
    def text(self):
        return self['text']

    @text.setter
    def text(self, value):
        self['text'] = value


class Button(ttk.Button, _Widget):

    def __init__(self, parent, **kwargs):
        ttk.Button.__init__(self, parent, **kwargs)

    @property
    def label(self):
        return self['text']

    @label.setter
    def label(self, value):
        self['text'] = value

    def on_click(self, callback):
        """Set an argument-less callback on the click event."""
        self['command'] = callback


class Checkbox(ttk.Checkbutton, _Widget):

    def __init__(self, parent, **kwargs):
        ttk.Checkbutton.__init__(self, parent, **kwargs)
        self._var = self['variable'] = tk.BooleanVar()
        self._var.set(False)

    @property
    def label(self):
        return self['text']

    @label.setter
    def label(self, value):
        self['text'] = value

    @property
    def checked(self):
        return self._var.get()

    @checked.setter
    def checked(self, value):
        self._var.set(value)

    def on_click(self, callback):
        """Set an argument-less callback on the click event."""
        self['command'] = callback


class Combobox(ttk.Combobox, _Widget):

    def __init__(self, parent, **kwargs):
        ttk.Combobox.__init__(self, parent, **kwargs)
        self.make_readonly()

    @property
    def values(self):
        return self['values']

    @values.setter
    def values(self, values):
        self['values'] = values or []
        self.set('')

    @property
    def selected_index(self):
        return self.current()

    @selected_index.setter
    def selected_index(self, index):
        self.current(index)

    @property
    def selected_value(self):
        return self['values'][self.selected_index]

    def on_select(self, callback):
        """Set a callback(event) on item select event."""
        self.bind('<<ComboboxSelected>>', callback)


class TextInput(ttk.Entry, _Widget):

    def __init__(self, parent, **kwargs):
        ttk.Entry.__init__(self, parent, **kwargs)
        self.bind_var(None)

    @property
    def text(self):
        return self._var.get() or ''

    @text.setter
    def text(self, value):

        state = str(self['state'])

        self.enable()
        self._var.set(value)

        if state != tk.NORMAL:
            self['state'] = state

    def set_password(self, flag=True):
        self['show'] = '*' if flag else ''

    def bind_var(self, variable):

        if not variable:
            variable = tk.StringVar()

        self._var = self['textvariable'] = variable


class TextArea(tk.Text, _Widget):

    def __init__(self, parent, **kwargs):
        tk.Text.__init__(self, parent, **kwargs)
        self.bind('<<Modified>>', self._on_edit)
        self._callback = None
        self.config(font=tkFont.Font(size=10))

    def make_readonly(self):
        self.disable()

    @property
    def text(self):
        return self.get(1.0, tk.END) or ''

    @text.setter
    def text(self, value):

        state = str(self['state'])

        self.enable()
        self.delete(1.0, tk.END)
        self.insert(1.0, value or '')

        if state != tk.NORMAL:
            self['state'] = state

    def on_edit(self, callback):
        """Set a callback(text) on text modified event."""
        self._callback = callback

    def _on_edit(self, event):

        if event.widget.edit_modified():
            if self._callback:
                self._callback(self.text.strip(' \t\n\r'))

        event.widget.edit_modified(False)


def show_error(message, title='Error'):
    tkMessageBox.showerror(title, message)
