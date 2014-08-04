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
Graphical user interface for microanalyst scripts.
"""

import os
import sys
import Tkinter as tk
import ttk

from microanalyst.gui import cmdwrapper
from microanalyst.gui import tkwidgets as tkw
from microanalyst.gui.tkwidgets import FileDialog


class Model(object):

    LAYOUTS = [
        'Single worksheet',
        'Multiple worksheets'
    ]

    LAYOUT_INFO = [
        'All microplates stacked vertically in one worksheet.',
        'Each microplate presented in a separate worksheet.'
    ]

    def __init__(self):
        self.iterations = []
        self.last_dir = os.getcwd()


class Controller(object):

    def __init__(self, view):

        self.model = Model()

        self.tab_iterations = view.tabs['iterations']
        self.tab_genes = view.tabs['genes']
        self.tab_summary = view.tabs['summary']

        nav_section = self.tab_iterations.nav_section
        nav_section.combobox.on_select(self.on_iterations_select)
        nav_section.new_button.on_click(self.on_new_button_click)
        nav_section.remove_button.on_click(self.on_remove_button_click)

        file_section = self.tab_iterations.file_section
        file_section.textarea.on_edit(self.on_textarea_edit)
        file_section.add_button.on_click(self.on_add_button_click)
        file_section.clear_button.on_click(self.on_clear_button_click)

        control_section = self.tab_iterations.control_section
        control_section.browse_button.on_click(self.on_browse_button_click)

        genes_section = self.tab_genes.genes_section
        genes_section.load_button.on_click(self.on_genes_load_button_click)
        genes_section.clear_button.on_click(self.on_genes_clear_button_click)

        layout_section = self.tab_summary.layout_section
        layout_section.combobox.on_select(self.on_layout_select)

        self.tab_summary.save_button.on_click(self.on_save_button_click)

    def on_iterations_select(self, event):

        index = event.widget.selected_index

        self._update_textarea(index)

        control_section = self.tab_iterations.control_section
        control_section.textinput.bind_var(self.model.iterations[index]['control'])

    def on_new_button_click(self):

        self.model.iterations.append({'files': [], 'control': tk.StringVar()})

        nav_section = self.tab_iterations.nav_section
        nav_section.combobox.values = self._get_iterations_names()
        nav_section.combobox.selected_index = len(self.model.iterations) - 1
        nav_section.remove_button.enable()

        file_section = self.tab_iterations.file_section
        file_section.textarea.text = ''
        file_section.textarea.enable()
        file_section.add_button.enable()
        file_section.clear_button.enable()

        control_section = self.tab_iterations.control_section
        control_section.textinput.bind_var(self.model.iterations[-1]['control'])
        control_section.textinput.enable()
        control_section.browse_button.enable()

        nav_section.combobox.focus()

        self._update_save_button()
        self.on_add_button_click()

    def on_remove_button_click(self):

        index = self._get_iteration_index()

        del self.model.iterations[index]

        file_section = self.tab_iterations.file_section
        file_section.textarea.text = ''

        nav_section = self.tab_iterations.nav_section
        nav_section.combobox.values = self._get_iterations_names()

        control_section = self.tab_iterations.control_section

        if len(self.model.iterations) == 0:

            nav_section.remove_button.disable()

            file_section.textarea.make_readonly()
            file_section.add_button.disable()
            file_section.clear_button.disable()

            control_section.textinput.bind_var(None)
            control_section.textinput.make_readonly()
            control_section.browse_button.disable()
        else:
            iterations = self.model.iterations[index - 1]

            nav_section.combobox.selected_index = max(0, index - 1)
            file_section.textarea.text = '\n'.join(iterations['files'])
            control_section.textinput.bind_var(iterations['control'])

        self._update_save_button()

    def on_textarea_edit(self, text):

        textarea = self.tab_iterations.file_section.textarea
        lines = textarea.text.strip(' \t\n\r').split('\n')

        index = self._get_iteration_index()
        self.model.iterations[index]['files'] = [x for x in lines if len(x) > 0]

        self._update_save_button()

    def on_add_button_click(self):

        filenames = tkw.FileDialog().open_files(self.model.last_dir)

        if filenames:

            index = self._get_iteration_index()

            self.model.last_dir = os.path.dirname(filenames[0])
            self.model.iterations[index]['files'] += [
                x for x in filenames if len(x) > 0
            ]

            self._update_textarea(index)

        self._update_save_button()

    def on_clear_button_click(self):
        self.tab_iterations.file_section.textarea.text = ''
        self._update_save_button()

    def on_browse_button_click(self):

        filename = tkw.FileDialog().open_file(self.model.last_dir,
                                              [FileDialog.FILTER_ALL,
                                               FileDialog.FILTER_JSON])

        if filename:

            index = self._get_iteration_index()

            self.model.last_dir = os.path.dirname(filename)
            self.model.iterations[index]['control'].set(filename)

    def on_genes_load_button_click(self):

        filename = tkw.FileDialog().open_file(self.model.last_dir,
                                              [FileDialog.FILTER_ALL,
                                               FileDialog.FILTER_JSON])

        if filename:
            with open(filename) as fh:
                self.tab_genes.genes_section.textarea.text = fh.read()

    def on_genes_clear_button_click(self):
        self.tab_genes.genes_section.textarea.text = ''

    def on_layout_select(self, event):
        layout_section = self.tab_summary.layout_section
        index = layout_section.combobox.selected_index
        layout_section.label.text = Model.LAYOUT_INFO[index]

    def on_save_button_click(self):

        filename = tkw.FileDialog().save(self.model.last_dir)

        if filename:

            self.model.last_dir = os.path.dirname(filename)

            genes = self.tab_genes.genes_section.textarea.text.strip()

            if genes == '':
                genes = None

            cmd = cmdwrapper.ScriptWrapper(self.model.iterations,
                                           filename,
                                           self.tab_summary.checkbox.checked,
                                           genes)

            index = self.tab_summary.layout_section.combobox.selected_index

            if index == 0:
                cmd.xlsv()
            else:
                cmd.xlsh()

    def _get_iteration_index(self):
        return self.tab_iterations.nav_section.combobox.selected_index

    def _get_iterations_names(self):
        return [
            'Iteration #%d' % (i + 1) for i in xrange(len(self.model.iterations))
        ]

    def _update_textarea(self, index):
        files = '\n'.join(self.model.iterations[index]['files'])
        self.tab_iterations.file_section.textarea.text = files

    def _update_save_button(self):
        if self._should_enable_save_button():
            self.tab_summary.save_button.enable()
        else:
            self.tab_summary.save_button.disable()

    def _should_enable_save_button(self):

        if len(self.model.iterations) == 0:
            return False

        for item in self.model.iterations:
            if len(item['files']) == 0:
                return False

        return True


class View(object):

    def __init__(self):

        self.window = tk.Tk()
        self.window.title('Microanalyst')

        self.tabs = {}

        notebook = ttk.Notebook(self.window)
        notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.tabs['iterations'] = IterationTab(notebook)
        self.tabs['genes'] = GenesTab(notebook)
        self.tabs['summary'] = SummaryTab(notebook)

        notebook.add(self.tabs['iterations'], text='Iterations')
        notebook.add(self.tabs['genes'], text='Genes')
        notebook.add(self.tabs['summary'], text='Summary')

        self.controller = Controller(self)

        self.window.mainloop()


class IterationTab(ttk.Frame):

    def __init__(self, parent):

        ttk.Frame.__init__(self, parent)

        self.nav_section = NavSection(self)
        self.file_section = FileSection(self)
        self.control_section = ControlSection(self)


class NavSection(ttk.Frame):

    def __init__(self, parent):

        ttk.Frame.__init__(self, parent, padding=5)

        tk.Grid.columnconfigure(self, 0, weight=1)

        self.combobox = tkw.Combobox(self)
        self.combobox.grid(row=0, column=0, padx=5, sticky=tk.W + tk.E)

        self.new_button = tkw.Button(self, text='New')
        self.new_button.grid(row=0, column=1, padx=5)

        self.remove_button = tkw.Button(self, text='Remove')
        self.remove_button.grid(row=0, column=2, padx=5)
        self.remove_button.disable()

        self.pack(anchor=tk.N, fill=tk.X, padx=5, pady=5)


class FileSection(ttk.LabelFrame):

    def __init__(self, parent):

        ttk.LabelFrame.__init__(self, parent, padding=5)
        self['text'] = 'Microplate spreadsheets'

        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

        self.textarea = tkw.TextArea(self)
        self.textarea.grid(row=0,
                           column=0,
                           columnspan=2,
                           padx=5,
                           pady=5,
                           sticky=tk.W + tk.E + tk.N + tk.S)
        self.textarea.disable()

        container = ttk.Frame(self)
        container.grid(row=1, column=1, sticky=tk.E)

        self.add_button = tkw.Button(container, text='Add...')
        self.add_button.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.add_button.disable()

        self.clear_button = tkw.Button(container, text='Clear')
        self.clear_button.grid(row=1, column=1, sticky=tk.E, padx=5, pady=5)
        self.clear_button.disable()

        self.pack(anchor=tk.N, expand=True, fill=tk.BOTH, padx=10, pady=5)


class ControlSection(ttk.LabelFrame):

    def __init__(self, parent):

        ttk.LabelFrame.__init__(self, parent, padding=5)
        self['text'] = 'Control wells (optional)'

        tk.Grid.columnconfigure(self, 0, weight=1)

        label = tkw.Label(self)
        label.grid(row=0, column=0, padx=5, sticky=tk.W)
        label.text = 'Text file with a JSON object inside, e.g. ' \
                     '{"002" : ["A4", "D5"], "003" : ["A4"]}'

        self.textinput = tkw.TextInput(self)
        self.textinput.grid(row=1,
                            column=0,
                            padx=5,
                            pady=5,
                            sticky=tk.W + tk.E)
        self.textinput.make_readonly()

        self.browse_button = tkw.Button(self, text='Browse...')
        self.browse_button.grid(row=1, column=1, padx=5, pady=5)
        self.browse_button.disable()

        self.pack(anchor=tk.N, fill=tk.X, padx=10, pady=5)


class GenesTab(ttk.Frame):

    def __init__(self, parent):

        ttk.Frame.__init__(self, parent)
        self.genes_section = GenesSection(self)


class GenesSection(ttk.LabelFrame):

    def __init__(self, parent):

        ttk.LabelFrame.__init__(self, parent, padding=5)
        self['text'] = 'Type definitions here, e.g. {"001": {"A1": "a", ' \
                       '"A2": "b"}, "002": {"H12": "c"}}'

        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

        self.textarea = tkw.TextArea(self)
        self.textarea.grid(row=0,
                           column=0,
                           columnspan=2,
                           padx=5,
                           pady=5,
                           sticky=tk.W + tk.E + tk.N + tk.S)

        container = ttk.Frame(self)
        container.grid(row=1, column=1, sticky=tk.E)

        self.load_button = tkw.Button(container, text='Load...')
        self.load_button.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)

        self.clear_button = tkw.Button(container, text='Clear')
        self.clear_button.grid(row=1, column=1, sticky=tk.E, padx=5, pady=5)

        self.pack(anchor=tk.N, expand=True, fill=tk.BOTH, padx=10, pady=5)


class SummaryTab(ttk.Frame):

    def __init__(self, parent):

        ttk.Frame.__init__(self, parent)

        self.layout_section = LayoutSection(self)

        self.checkbox = tkw.Checkbox(self)
        self.checkbox.pack(anchor=tk.W, padx=10)
        self.checkbox.label = 'Keep intermediate JSON assembly.'

        self.save_button = tkw.Button(self, text='Save as...')
        self.save_button.pack(anchor=tk.S, side=tk.RIGHT, padx=10, pady=5)
        self.save_button.disable()


class LayoutSection(ttk.LabelFrame):

    def __init__(self, parent):

        ttk.LabelFrame.__init__(self, parent, padding=5, text='Layout')

        self.label = tkw.Label(self)
        self.label.pack(anchor=tk.W, padx=5)
        self.label.text = Model.LAYOUT_INFO[0]

        self.combobox = tkw.Combobox(self)
        self.combobox.pack(anchor=tk.N, expand=True, fill=tk.X, padx=5, pady=2)
        self.combobox.values = Model.LAYOUTS
        self.combobox.selected_index = 0

        self.pack(anchor=tk.N, fill=tk.X, padx=10, pady=10)


if __name__ == '__main__':
    try:
        View()
    except KeyboardInterrupt:
        print >> sys.stderr, 'Aborted'
