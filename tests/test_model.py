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
import numpy

from random import random
from microanalyst.model import Model
from microanalyst.model.genes import Gene


class TestFilenames(unittest.TestCase):

    def test_show_full_path_by_default(self):

        # given
        model = TestModel.with_filenames(
            ['C:\\windows style\\path\\foo.xls', 'relative\\path\\bar.xls'],
            ['/unix style/path/baz.xls', 'relative/path/blah'])

        # when
        actual = model.filenames()

        # then
        self.assertListEqual(
            ['C:\\windows style\\path\\foo.xls',
             'relative\\path\\bar.xls',
             '/unix style/path/baz.xls',
             'relative/path/blah'],
            actual)

    def test_drop_windows_style_path(self):

        # given
        model = TestModel.with_filenames(
            ['C:\\windows\style.xls', 'foo\\bar.xls'],
            ['blah\\blah.txt'])

        # when
        actual = model.filenames(with_path=False)

        # then
        self.assertListEqual(['style.xls', 'bar.xls', 'blah.txt'], actual)

    def test_drop_unix_style_path(self):

        # given
        model = TestModel.with_filenames(
            ['/unix/style.xls', 'foo/bar.xls'],
            ['blah/blah.txt'])

        # when
        actual = model.filenames(with_path=False)

        # then
        self.assertListEqual(['style.xls', 'bar.xls', 'blah.txt'], actual)

    def test_drop_unix_and_windows_style_path(self):

        # given
        model = TestModel.with_filenames(
            ['C:\\windows\\style.xls', 'foo/bar.xls'],
            ['blah\\blah.txt'])

        # when
        actual = model.filenames(with_path=False)

        # then
        self.assertListEqual(['style.xls', 'bar.xls', 'blah.txt'], actual)

    def test_show_only_filenames_for_the_given_iteration(self):

        # given
        model = TestModel.with_filenames(
            ['i1/f1', 'i1/f2'],
            ['i2/f1', 'i2/f2', 'i2/f3'],
            ['i3/f1'])

        # when
        actual = model.filenames(iteration=1)

        # then
        self.assertIn('i2/f1', actual)
        self.assertIn('i2/f2', actual)
        self.assertIn('i2/f3', actual)

    def test_retain_filename_order_for_the_given_iteration(self):

        # given
        model = TestModel.with_filenames(
            ['i1/f1', 'i1/f2'],
            ['i2/f1', 'i2/f2', 'i2/f3'],
            ['i3/f1'])

        # when
        actual = model.filenames(iteration=1)

        # then
        self.assertListEqual(['i2/f1', 'i2/f2', 'i2/f3'], actual)

    def test_retain_filename_order_across_all_iterations(self):

        # given
        model = TestModel.with_filenames(
            ['i1/f1', 'i1/f2'],
            ['i2/f1', 'i2/f2', 'i2/f3'],
            ['i3/f1'])

        # when
        actual = model.filenames()

        # then
        self.assertListEqual(
            ['i1/f1', 'i1/f2', 'i2/f1', 'i2/f2', 'i2/f3', 'i3/f1'],
            actual)

    def test_retain_duplicate_filenames_from_different_folders(self):

        # given
        model = TestModel.with_filenames(['folder1/filename',
                                          'folder2/filename'])

        # when
        actual = model.filenames(with_path=False)

        # then
        self.assertListEqual(['filename', 'filename'], actual)

    def test_do_not_confuse_iterations_zero_index_for_none(self):

        # given
        model = TestModel.with_filenames(
            ['i1/f1', 'i1/f2'],
            ['i2/f1', 'i2/f2', 'i2/f3'],
            ['i3/f1'])

        # when
        actual = model.filenames(iteration=0)

        # then
        self.assertListEqual(['i1/f1', 'i1/f2'], actual)

    def test_each_invocation_should_return_a_copy(self):

        # given
        model = TestModel.with_filenames(
            ['i1/f1', 'i1/f2'],
            ['i2/f1', 'i2/f2', 'i2/f3'],
            ['i3/f1'])

        # when
        copy1 = model.filenames()
        copy2 = model.filenames()

        # then
        self.assertNotEqual(id(copy1), id(copy2))

    def test_each_invocation_should_return_the_same_result(self):

        # given
        model = TestModel.with_filenames(
            ['i1/f1', 'i1/f2'],
            ['i2/f1', 'i2/f2', 'i2/f3'],
            ['i3/f1'])

        # when
        copy1 = model.filenames()
        copy2 = model.filenames()

        # then
        self.assertListEqual(copy1, copy2)

    def test_return_flat_list_if_no_iteration_specified(self):

        # given
        model = TestModel.with_filenames(
            ['i1/f1', 'i1/f2'],
            ['i2/f1', 'i2/f2', 'i2/f3'],
            ['i3/f1'])

        # when
        actual = model.filenames()

        # then
        for item in actual:
            self.assertIsInstance(item, str)

    def test_allow_variable_number_of_filenames_across_iterations(self):

        # given
        model = TestModel.with_filenames(
            ['i1/f1', 'i1/f2'],
            ['i2/f1', 'i2/f2', 'i2/f3'],
            ['i3/f1'])

        # then
        for i, length in enumerate((2, 3, 1)):
            self.assertEqual(length, len(model.filenames(iteration=i)))

    def test_raise_error_if_spreadsheet_has_no_filename_defined(self):

        # given
        json_data = {
            'iterations': [
                {
                    'spreadsheets': [
                        {
                            'filename': 'ok',
                            'microplates': {}
                        },
                        {
                            'microplates': {}
                        }
                    ]
                }
            ]
        }

        # then
        with self.assertRaises(KeyError):
            # when
            model = Model(json_data)


class TestMicroplateNames(unittest.TestCase):

    def test_return_empty_list_for_an_empty_model(self):

        # given
        model = TestModel.empty()

        # when
        actual = model.microplate_names()

        # then
        self.assertListEqual([], actual)

    def test_return_unique_microplate_names(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['001', '002', '003'], ['007']])

        # when
        actual = model.microplate_names()

        # then
        self.assertItemsEqual(set(actual), actual)

    def test_return_sorted_microplate_names(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['011', '012', '013'], ['017']])

        # when
        actual = model.microplate_names()

        # then
        self.assertListEqual(sorted(actual), actual)

    def test_return_flat_list_if_no_spreadsheet_nor_iteration_defined(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['011', '012', '013'], ['017']])

        # when
        actual = model.microplate_names()

        # then
        for item in actual:
            self.assertIsInstance(item, str)

    def test_return_flat_list_if_only_iteration_defined(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['011', '012', '013'], ['017']])

        # when
        actual = model.microplate_names(iteration=1)

        # thens
        for item in actual:
            self.assertIsInstance(item, str)

    def test_return_flat_list_if_only_spreadsheet_defined(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['011', '012', '013'], ['017']])

        # when
        actual = model.microplate_names(spreadsheet=1)

        # thens
        for item in actual:
            self.assertIsInstance(item, str)

    def test_return_flat_list_if_both_spreadsheet_and_iteration_defined(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['011', '012', '013'], ['017']])

        # when
        actual = model.microplate_names(iteration=1, spreadsheet=1)

        # thens
        for item in actual:
            self.assertIsInstance(item, str)

    def test_do_not_confuse_iterations_zero_index_for_none(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['011', '012', '013'], ['017']])

        # when
        actual = model.microplate_names(iteration=0)

        # thens
        self.assertListEqual(['001', '002', '003'], actual)

    def test_do_not_confuse_spreadsheets_zero_index_for_none(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['011', '012', '013'], ['017']])

        # when
        actual = model.microplate_names(spreadsheet=0)

        # thens
        self.assertListEqual(['001', '002', '011', '012', '013'], actual)

    def test_pick_specified_iteration(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002']],
            [['011', '012', '013'], ['017']],
            [['021', '022', '023'], ['027'], ['029']])

        # when
        actual = model.microplate_names(iteration=1)

        # then
        self.assertListEqual(['011', '012', '013', '017'], actual)

    def test_raise_error_when_specified_iteration_doesnt_exist(self):

        # given
        model = TestModel.with_microplates([['001']])

        # then
        with self.assertRaises(IndexError):
            # when
            model.microplate_names(iteration=1)

    def test_pick_both_specified_iteration_and_spreadsheet(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002']],
            [['011', '012', '013'], ['017']],
            [['021', '022', '023'], ['025', '027'], ['029']])

        # when
        actual = model.microplate_names(iteration=2, spreadsheet=1)

        # then
        self.assertListEqual(['025', '027'], actual)

    def test_raise_error_when_specified_iteration_doesnt_exist_but_spreadsheet_does(
            self):

        # given
        model = TestModel.with_microplates([['001', '002'], ['011', '012']])

        # then
        with self.assertRaises(IndexError):
            # when
            model.microplate_names(iteration=1, spreadsheet=1)

    def test_raise_error_when_specified_spreadsheet_doesnt_exist_but_iteration_does(self):

        # given
        model = TestModel.with_microplates([['001', '002'], ['011', '012']])

        # then
        with self.assertRaises(IndexError):
            # when
            model.microplate_names(iteration=0, spreadsheet=2)

    def test_pick_specified_spreadsheet(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['011', '012', '013'], ['017']],
            [['021', '022', '023'], ['025', '027'], ['029']])

        # when
        actual = model.microplate_names(spreadsheet=1)

        # then
        self.assertListEqual(['001', '002', '003', '017', '025', '027'], actual)

    def test_raise_error_if_spreadsheet_doesnt_exist(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['011', '012', '013'], ['017']])

        # then
        with self.assertRaises(IndexError):

            # when
            actual = model.microplate_names(spreadsheet=5)

    def test_omit_missing_spreadsheet(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['011', '012', '013'], ['017']],
            [['021', '022', '023'], ['025', '027'], ['028', '029']])

        # when
        actual = model.microplate_names(spreadsheet=2)

        # then
        self.assertListEqual(['028', '029'], actual)

    def test_pick_all_microplates(self):

        # given
        model = TestModel.with_microplates(
            [['001', '002'], ['001', '002', '003']],
            [['011', '012', '013'], ['017']],
            [['021', '022', '023'], ['025', '027'], ['028', '029']])

        # when
        actual = model.microplate_names()

        # then
        self.assertListEqual(
            ['001', '002', '003', '011', '012',
             '013', '017', '021', '022', '023',
             '025', '027', '028', '029'],
            actual)

    def test_allow_variable_number_of_microplates_per_iteration(self):

        # given
        model = TestModel.with_microplates(
            [['001'], ['001', '002'], ['001', '002', '003']],
            [['011'], ['011', '012'], ['011', '012', '013']])

        # when
        actual = model.microplate_names(iteration=1)

        # then
        self.assertListEqual(['011', '012', '013'], actual)

    def test_allow_variable_number_of_microplates_per_spreadsheet(self):

        # given
        model = TestModel.with_microplates(
            [['001'], ['001', '002'], ['001', '002', '003']],
            [['001', '002'], ['001', '002', '003'], ['011', '012', '013']])

        # when
        actual = model.microplate_names(spreadsheet=1)

        # then
        self.assertListEqual(['001', '002', '003'], actual)

    def test_each_invocation_should_return_a_copy(self):

        # given
        model = TestModel.with_microplates(
            [['001'], ['001', '002'], ['001', '002', '003']],
            [['011'], ['011', '012'], ['011', '012', '013']])

        # when
        copy1 = model.microplate_names()
        copy2 = model.microplate_names()

        # then
        self.assertNotEqual(id(copy1), id(copy2))

    def test_each_invocation_should_return_the_same_result(self):

        # given
        model = TestModel.with_microplates(
            [['001'], ['001', '002'], ['001', '002', '003']],
            [['011'], ['011', '012'], ['011', '012', '013']])

        # when
        copy1 = model.microplate_names()
        copy2 = model.microplate_names()

        # then
        self.assertListEqual(copy1, copy2)


class TestGenes(unittest.TestCase):

    def test_return_microplate_well_tuple_for_gene(self):

        # given
        model = TestModel.with_genes({'001': {'A1': 'foobar'}})
        genes = model.genes()

        # when
        gene = genes[0]
        microplate, well = gene()

        # then
        self.assertEqual('foobar', str(gene))
        self.assertEqual('001', microplate)
        self.assertEqual('A1', well)

    def test_return_empty_list_if_no_genes_defined_in_json(self):

        # given
        model = TestModel.empty()

        # when/then
        self.assertListEqual([], model.genes())
        self.assertListEqual([], model.genes(well='A1'))
        self.assertListEqual([], model.genes(microplate='001'))
        self.assertListEqual([], model.genes(well='A1', microplate='001'))

    def test_each_invocation_should_return_a_copy(self):

        # given
        model = TestModel.with_genes({'001': {'A1': 'foobar'}})

        # when
        copy1 = model.genes()
        copy2 = model.genes()

        # then
        self.assertNotEqual(id(copy1), id(copy2))

    def test_each_invocation_should_return_the_same_result(self):

        # given
        model = TestModel.with_genes({'001': {'A1': 'foobar'}})

        # when
        copy1 = model.genes()
        copy2 = model.genes()

        # then
        self.assertEqual(copy1, copy2)

    def test_return_sorted_gene_names(self):

        # given
        model = TestModel.with_genes({
            '001': {
                'A1': 'def',
                'A2': 'abc',
                'A3': '123'
            },
            '002': {
                'A7': 'abc',
                'H12': 'ghij'
            }
        })

        # when
        actual = model.genes()

        # then
        self.assertItemsEqual(sorted(actual), actual)

    def test_return_unique_gene_names(self):

        # given
        model = TestModel.with_genes({
            '001': {
                'A1': 'def',
                'A2': 'abc',
                'A3': '123'
            },
            '002': {
                'A7': 'abc',
                'H12': 'ghij'
            }
        })

        # when
        actual = model.genes()

        # then
        self.assertItemsEqual(set(actual), actual)

    def test_return_flat_list_if_no_microplate_nor_well_specified(self):

        # given
        model = TestModel.with_genes({
            '001': {
                'A1': 'def',
                'A2': 'abc',
                'A3': '123'
            },
            '002': {
                'A7': 'abc',
                'H12': 'ghij'
            }
        })

        # when
        actual = model.genes()

        # then
        for item in actual:
            self.assertIsInstance(item, Gene)

    def test_return_flat_list_if_only_well_specified(self):

        # given
        model = TestModel.with_genes({
            '001': {
                'A1': 'def',
                'A2': 'abc',
                'A3': '123'
            },
            '002': {
                'A1': 'foo',
                'A7': 'abc',
                'H12': 'ghij'
            }
        })

        # when
        actual = model.genes(well='A1')

        # then
        for item in actual:
            self.assertIsInstance(item, Gene)

    def test_return_flat_list_if_only_microplate_specified(self):

        # given
        model = TestModel.with_genes({
            '001': {
                'A1': 'def',
                'A2': 'abc',
                'A3': '123'
            },
            '002': {
                'A1': 'foo',
                'A7': 'abc',
                'H12': 'ghij'
            }
        })

        # when
        actual = model.genes(microplate='001')

        # then
        for item in actual:
            self.assertIsInstance(item, Gene)

    def test_remove_none_values_from_the_resulting_list(self):

        # given
        model = TestModel.with_genes({
            '001': {
                'A1': 'def',
                'A2': 'abc',
                'A3': '123'
            },
            '002': {
                'A1': 'foo',
                'A7': 'abc',
                'H12': 'ghij'
            }
        })

        # when
        actual = model.genes(microplate='001')

        # then
        self.assertNotIn(None, actual)

    def test_remove_none_value_from_the_resulting_one_element_list(self):

        # given
        model = TestModel.with_genes({
            '001': {
                'A1': 'def',
                'A2': 'abc',
                'A3': '123'
            },
            '002': {
                'A1': 'foo',
                'A7': 'abc',
                'H12': 'ghij'
            }
        })

        # when
        actual = model.genes(well='A4', microplate='001')

        # then
        self.assertNotIn(None, actual)

    def test_return_one_element_list_if_both_well_and_microplate_specified(self):

        # given
        model = TestModel.with_genes({
            '001': {
                'A1': 'def',
                'A2': 'abc',
                'A3': '123'
            },
            '002': {
                'A1': 'foo',
                'A7': 'abc',
                'H12': 'ghij'
            }
        })

        # when
        actual = model.genes(well='A3', microplate='001')

        # then
        self.assertIsInstance(actual, list)
        self.assertEqual(1, len(actual))

    def test_return_scalar_for_unambiguous_gene(self):

        # given
        model = TestModel.with_genes({'001':{'A1':'foobar'}})

        # when
        actual = model.gene_at('A1', '001')

        # then
        self.assertIsInstance(actual, Gene)

    def test_return_none_for_missing_unambiguous_gene(self):

        # given
        model = TestModel.with_genes({'001':{'A1':'foobar'}})

        # when
        actual = model.gene_at('A2', '001')

        # then
        self.assertIsNone(actual)

    def test_show_genes_for_a_microplate_missing_from_the_iterations(self):

        # given
        model = Model({
            'genes': {
                '666': {
                    'A1': 'blah',
                    'A2': 'halb'
                }
            },
            'iterations': [
                {
                    'spreadsheets': [
                        {
                            'filename': 'foo.xls',
                            'microplates': {
                                '001': {
                                    'values': []
                                }
                            }
                        }
                    ]
                }
            ]
        })

        # when
        actual = model.genes(microplate='666')

        # then
        self.assertListEqual(['blah', 'halb'], sorted([str(x) for x in actual]))

    def test_return_empty_list_for_a_microplate_available_in_iterations_but_not_in_genes(self):

        # given
        model = Model({
            'genes': {
                '666': {
                    'A1': 'blah',
                    'A2': 'halb'
                }
            },
            'iterations': [
                {
                    'spreadsheets': [
                        {
                            'filename': 'foo.xls',
                            'microplates': {
                                '001': {
                                    'values': []
                                }
                            }
                        }
                    ]
                }
            ]
        })

        # when
        actual = model.genes(microplate='001')

        # then
        self.assertListEqual([], actual)

    def test_raise_error_for_a_microplate_not_available_in_iterations_nor_genes(self):

        # given
        model = Model({
            'genes': {
                '666': {
                    'A1': 'blah',
                    'A2': 'halb'
                }
            },
            'iterations': [
                {
                    'spreadsheets': [
                        {
                            'filename': 'foo.xls',
                            'microplates': {
                                '001': {
                                    'values': []
                                }
                            }
                        }
                    ]
                }
            ]
        })

        # then
        with self.assertRaises(KeyError):

            # when
            actual = model.genes(microplate='777')

    def test_well_addressing(self):

        # given
        model = TestModel.with_genes({'001':{'C10':'foobar'}})

        # when
        copy1 = model.genes(well='C10')
        copy2 = model.genes(well=33)

        # then
        self.assertListEqual(copy1, copy2)

    def test_return_empty_list_if_well_not_present_in_genes(self):

        # given
        model = TestModel.with_genes({'001':{'C10':'foobar'}})

        # when
        actual = model.genes(well='A1')

        # then
        self.assertListEqual([], actual)

    def test_return_empty_list_for_genes_used_if_no_genes_defined(self):

        # given
        model = TestModel.with_microplates(['001', '002'], ['001', '002', '003'])

        # when
        actual = model.genes_used()

        # then
        self.assertListEqual([], actual)

    def test_return_empty_list_for_genes_used_if_no_microplates_defined(self):

        # given
        model = TestModel.with_genes({'001': {'A1': 'foobar'}})

        # when
        actual = model.genes_used()

        # then
        self.assertListEqual([], actual)

    def test_return_subset_for_genes_used(self):

        # given
        model = Model({
            'genes': {
                '001': {
                    'A1': 'blah'
                },
                'B002': {
                    'A1': 'dummy'
                }
            },
            'iterations': [
                {
                    'spreadsheets': [
                        {
                            'filename': 'foo.xls',
                            'microplates': {
                                '001': {
                                    'values': []
                                }
                            }
                        }
                    ]
                }
            ]
        })

        # when
        num_used = len(model.genes_used())
        num_all = len(model.genes())

        # then
        self.assertTrue(num_used < num_all)

    def test_do_not_confuse_iteration_zero_index_for_none(self):

        # given
        genes = {'001': {'A5': 'foo'}, '002': {'G11': 'bar'}}

        iterations = TestModel.with_random_values(
           [['001', '002'], ['001', '002']],
           [['001', '002'], ['001', '002']]
        ).json_data['iterations']

        model = Model({'genes': genes, 'iterations': iterations})

        # when
        copy1 = model.genes()[0].values(iteration=0, spreadsheet=0)
        copy2 = model.genes()[0].values(iteration=None, spreadsheet=0)

        # then
        self.assertFalse((copy1 == copy2).all())

    def test_do_not_confuse_spreadsheet_zero_index_for_none(self):

        # given
        genes = {'001': {'A5': 'foo'}, '002': {'G11': 'bar'}}

        iterations = TestModel.with_random_values(
           [['001', '002'], ['001', '002']],
           [['001', '002'], ['001', '002']]
        ).json_data['iterations']

        model = Model({'genes': genes, 'iterations': iterations})

        # when
        copy1 = model.genes()[0].values(spreadsheet=0, iteration=0)
        copy2 = model.genes()[0].values(spreadsheet=None, iteration=0)

        # then
        self.assertFalse((copy1 == copy2).all())

    def test_return_same_values_as_with_model_values(self):

        # given
        genes = {'001': {'A5': 'foo'}, '002': {'G11': 'bar'}}

        iterations = TestModel.with_random_values(
           [['001', '002'], ['001', '002']],
           [['001', '002'], ['001', '002']]
        ).json_data['iterations']

        model = Model({'genes': genes, 'iterations': iterations})

        # when
        for gene in model.genes():

            actual = gene.values()
            expected = model.values(microplate=gene.microplate_name, well=gene.well_name)

            # then
            self.assertTrue((actual == expected).all())

    def test_return_scalar_if_both_parameters_are_specified(self):

        # given
        genes = {'001': {'A5': 'foo'}, '002': {'G11': 'bar'}}

        iterations = TestModel.with_random_values(
           [['001', '002'], ['001', '002']],
           [['001', '002'], ['001', '002']]
        ).json_data['iterations']

        model = Model({'genes': genes, 'iterations': iterations})

        # when
        actual = model.genes()[0].values(iteration=0, spreadsheet=0)

        # then
        self.assertIsInstance(actual, float)

    def test_representative_values_for_an_iteration_filter(self):

        # given
        genes = {'001': {'A5': 'foo'}, '002': {'G11': 'bar'}}

        iterations = TestModel.with_random_values(
           [['001', '002'], ['001', '002']],
           [['001', '002'], ['001', '002']]
        ).json_data['iterations']

        model = Model({'genes': genes, 'iterations': iterations})

        # when
        for gene in model.genes():

            actual = gene.values(iteration=1)
            expected = model.values(iteration=1,
                                    microplate=gene.microplate_name,
                                    well=gene.well_name)

            # then
            self.assertTrue((actual == expected).all())

    def test_representative_values_for_a_spreadsheet_filter(self):

        # given
        genes = {'001': {'A5': 'foo'}, '002': {'G11': 'bar'}}

        iterations = TestModel.with_random_values(
           [['001', '002'], ['001', '002']],
           [['001', '002'], ['001', '002']]
        ).json_data['iterations']

        model = Model({'genes': genes, 'iterations': iterations})

        # when
        for gene in model.genes():

            actual = gene.values(spreadsheet=1)
            expected = model.values(spreadsheet=1,
                                    microplate=gene.microplate_name,
                                    well=gene.well_name)

            # then
            self.assertTrue((actual == expected).all())

    def test_get_gene_by_name_case_insensitive(self):

        # given
        model = TestModel.with_genes({'001': {'A1': 'tORF9', 'A2': 'foo'}})

        # when
        actual = model.gene('torf9')

        # then
        self.assertEqual('tORF9', actual.name)

    def test_return_none_if_gene_name_not_found(self):

        # given
        model = TestModel.with_genes({'001': {'A1': 'foo', 'A2': 'bar'}})

        # when
        actual = model.gene('baz')

        # then
        self.assertIsNone(actual)

    def test_return_first_gene_if_duplicates_found(self):

        # given
        model = TestModel.with_genes({
            '001': {
                'A1': 'foo',
                'A2': 'bar',
                'H12': 'foo'
            },
            '002': {
                'A4': 'baz'
            },
            '003': {
                'E4': 'foo'
            }
        })

        # when
        actual = model.gene('foo')

        # then
        self.assertEqual('001', actual.microplate_name)
        self.assertEqual('A1', actual.well_name)


class TestValues(unittest.TestCase):

    def test_return_scalar_if_all_parameters_are_specified(self):

        # given
        model = TestModel.with_random_values([['001', '002'], ['001']])

        # when
        actual = model.values(iteration=0,
                              spreadsheet=0,
                              microplate='001',
                              well='A1')

        # then
        self.assertIsInstance(actual, float)

    def test_return_numpy_ndarray_if_any_parameter_is_missing(self):

        # given
        model = TestModel.with_random_values([['001', '002'], ['001']])

        # when/then
        self.assertIsInstance(model.values(), numpy.ndarray)

        self.assertIsInstance(model.values(iteration=0), numpy.ndarray)
        self.assertIsInstance(model.values(spreadsheet=0), numpy.ndarray)
        self.assertIsInstance(model.values(microplate='001'), numpy.ndarray)

        self.assertIsInstance(model.values(iteration=0, spreadsheet=0), numpy.ndarray)
        self.assertIsInstance(model.values(iteration=0, microplate='001'), numpy.ndarray)
        self.assertIsInstance(model.values(spreadsheet=0, microplate='001'), numpy.ndarray)

        self.assertIsInstance(model.values(iteration=0, spreadsheet=0, microplate='001'), numpy.ndarray)

    def test_return_array4d(self):

        # given
        model = TestModel.with_random_values([['001', '002'], ['001']])

        # when
        actual = model.values()

        # then
        self.assertEqual(4, actual.ndim)

    def test_return_array3d(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001']], [['001']])

        # when/then
        self.assertEqual(3, model.values(iteration=1).ndim)
        self.assertEqual(3, model.values(spreadsheet=1).ndim)
        self.assertEqual(3, model.values(microplate='001').ndim)

    def test_return_array2d(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001']], [['001']])

        # when/then
        self.assertEqual(2, model.values(iteration=1, spreadsheet=1).ndim)
        self.assertEqual(2, model.values(iteration=1, microplate='001').ndim)
        self.assertEqual(2, model.values(spreadsheet=1, microplate='001').ndim)

    def test_return_array1d(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001']], [['001']])

        # when
        actual = model.values(iteration=1, spreadsheet=1, microplate='001')

        # then
        self.assertEqual(1, actual.ndim)

    def test_return_original_array_if_no_parameter_is_specified(self):

        # given
        model = TestModel.with_random_values([['001', '002'], ['001']])

        # when
        actual = model.values()

        # then
        self.assertTrue((actual == model.array4d).all())

    def test_retain_none_values(self):

        # given
        model = TestModel.with_random_values([['001', '002'], ['001']])

        # when
        actual = model.values(spreadsheet=1)

        # then
        self.assertIn(None, list(actual[0][1]))

    def test_each_invocation_should_return_a_copy(self):

        # given
        model = TestModel.with_random_values([['001', '002'], ['001']])

        # when
        copy1 = model.values(well='A1')
        copy2 = model.values(well='A1')

        # then
        self.assertNotEqual(id(copy1), id(copy2))

    def test_each_invocation_should_return_the_same_result(self):

        # given
        model = TestModel.with_random_values([['001', '002'], ['001']])

        # when
        copy1 = model.values(well='A1')
        copy2 = model.values(well='A1')

        # then
        self.assertTrue((copy1 == copy2).all())

    def test_well_addressing(self):

        # given
        model = TestModel.with_random_values([['001', '002'], ['001']])

        # when
        copy1 = model.values(well='C10')
        copy2 = model.values(well=33)

        # then
        self.assertTrue((copy1 == copy2).all())

    def test_microplate_addressing(self):

        # given
        model = TestModel.with_random_values([['001', '002'], ['001']])

        # when
        copy1 = model.values(microplate='002')
        copy2 = model.values(microplate=1)

        # then
        self.assertTrue((copy1 == copy2).all())

    def test_do_not_confuse_iteration_zero_index_for_none(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['003'], ['001', '004']])

        # when
        copy1 = model.values(iteration=0, microplate='001', well='A1')
        copy2 = model.values(iteration=None, microplate='001', well='A1')

        # then
        self.assertFalse((copy1 == copy2).all())

    def test_do_not_confuse_spreadsheet_zero_index_for_none(self):

        # given
        model = TestModel.with_random_values([['001', '002'], ['001']])

        # when
        copy1 = model.values(spreadsheet=0, well='A1', iteration=0, microplate='001')
        copy2 = model.values(spreadsheet=None, well='A1', iteration=0, microplate='001')

        # then
        self.assertFalse((copy1 == copy2).all())

    def test_do_not_confuse_well_zero_index_for_none(self):

        # given
        model = TestModel.with_random_values([['001', '002'], ['001']])

        # when
        copy1 = model.values(well=0, iteration=0, spreadsheet=0, microplate='001')
        copy2 = model.values(well=None, iteration=0, spreadsheet=0, microplate='001')

        # then
        self.assertFalse((copy1 == copy2).all())

    def test_variable_number_of_microplates_across_spreadsheets(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002', '003'],
             ['001', '003'],
             ['001', '002', '003', '004']])

        # when
        actual = model.values(microplate='002', spreadsheet=1, well='A1')

        # then
        self.assertListEqual([None], list(actual))

    def test_variable_number_of_spreadsheets_across_iterations(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002']])

        # when
        actual = model.values(microplate='002', spreadsheet=1, well='A1')

        # then
        x = model.values(iteration=0, microplate='002', spreadsheet=1, well='A1')
        self.assertListEqual([x, None], list(actual))

    def test_pad_missing_spreadsheets_with_empty_stubs(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002']])

        # when
        iterations = model.json_data[u'iterations']
        num_spreadsheets = [len(x[u'spreadsheets']) for x in iterations]
        max_spreadsheets = max(num_spreadsheets)
        min_spreadsheets = min(num_spreadsheets)

        def get_microplates(i, j):
            return iterations[i][u'spreadsheets'][j][u'microplates']

        # then
        self.assertTrue(min_spreadsheets == max_spreadsheets == 2)
        self.assertEqual({}, get_microplates(1, 1))

    def test_dont_pad_spreadsheets_if_not_missing(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['003', '004']],
            [['011', '012'], ['013', '014']])

        # when
        iterations = model.json_data[u'iterations']
        num_spreadsheets = [len(x[u'spreadsheets']) for x in iterations]
        max_spreadsheets = max(num_spreadsheets)
        min_spreadsheets = min(num_spreadsheets)

        def get_microplates(i, j):
            return iterations[i][u'spreadsheets'][j][u'microplates']

        # then
        self.assertTrue(min_spreadsheets == max_spreadsheets == 2)
        self.assertNotEqual({}, get_microplates(0, 0))
        self.assertNotEqual({}, get_microplates(0, 1))
        self.assertNotEqual({}, get_microplates(1, 0))
        self.assertNotEqual({}, get_microplates(1, 1))

    def test_return_none_if_no_iterations_available_in_JSON(self):

        # given
        model = TestModel.with_genes({})

        # when
        actual = model.values()

        # then
        self.assertEqual(None, actual)

    def test_representative_value_for_an_iteration_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        iteration = model.values(iteration=1)
        spreadsheet = iteration[1]
        microplate = spreadsheet[1]
        well = microplate[48]

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], well)

    def test_representative_value_for_a_spreadsheet_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        spreadsheet = model.values(spreadsheet=1)
        spreadsheet_within_iteration = spreadsheet[1]
        microplate = spreadsheet_within_iteration[1]
        well = microplate[48]

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], well)

    def test_representative_value_for_a_microplate_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        microplate = model.values(microplate='002')
        microplate_within_iteration = microplate[1]
        microplate_within_iteration_and_spreadsheet = microplate_within_iteration[1]
        well = microplate_within_iteration_and_spreadsheet[48]

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], well)

    def test_representative_value_for_a_well_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        well = model.values(well='E1')
        well_within_iteration = well[1]
        well_within_iteration_and_spreadsheet = well_within_iteration[1]
        well_within_iteration_spreadsheet_and_microplate = well_within_iteration_and_spreadsheet[1]

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], well_within_iteration_spreadsheet_and_microplate)

    def test_representative_value_for_microplate_well_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        microplates = model.values(microplate='002', well='E1')
        wells = microplates[1]

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], wells[1])

    def test_representative_value_for_spreadsheet_well_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        spreadsheet = model.values(spreadsheet=1, well='E1')
        microplate = spreadsheet[1]

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], microplate[1])

    def test_representative_value_for_spreadsheet_microplate_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        microplate_in_spreadsheets = model.values(spreadsheet=1, microplate='002')
        microplate = microplate_in_spreadsheets[1]

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], microplate[48])

    def test_representative_value_for_iteration_well_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        wells = model.values(iteration=1, well='E1')
        wells_within_iteration = wells[1]

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], wells_within_iteration[1])

    def test_representative_value_for_iteration_microplate_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        microplates = model.values(iteration=1, microplate='002')
        microplate_within_iteration = microplates[1]

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], microplate_within_iteration[48])

    def test_representative_value_for_iteration_spreadsheet_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        spreadsheet = model.values(iteration=1, spreadsheet=1)
        microplate = spreadsheet[1]

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], microplate[48])

    def test_representative_value_for_spreadsheet_microplate_well_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        wells = model.values(spreadsheet=1, microplate='002', well='E1')

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], wells[1])

    def test_representative_value_for_iteration_microplate_well_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        wells = model.values(iteration=1, microplate='002', well='E1')

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], wells[1])

    def test_representative_value_for_iteration_spreadsheet_well_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        wells = model.values(iteration=1, spreadsheet=1, well='E1')

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], wells[1])

    def test_representative_value_for_iteration_spreadsheet_microplate_filter(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        microplate = model.values(iteration=1, spreadsheet=1, microplate='002')

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], microplate[48])

    def test_representative_value_for_all_filters(self):

        # given
        model = TestModel.with_random_values(
            [['001', '002'], ['001', '002']],
            [['001', '002'], ['001', '002']])

        # when
        actual = model.values(iteration=1, spreadsheet=1, microplate='002', well='E1')

        # then
        self.assertEqual(model.array4d[1, 1, 1, 48], actual)


class TestControl(unittest.TestCase):

    def test_microplate_addressing(self):

        # given
        model = TestModel.with_control_wells(
            {'001': ['A1', 'A2'], '002': ['A4']},
            {'001': ['C1', 'C2'], '002': ['C4']})

        # when
        copy1 = model.control_mask(microplate='002')
        copy2 = model.control_mask(microplate=1)

        # then
        self.assertTrue((copy1 == copy2).all())

    def test_none_mask_if_no_control_wells(self):

        # given
        model = TestModel.empty()

        # when
        actual = model.control_mask

        # then
        self.assertIsNotNone(actual)
        self.assertIsNone(actual.values)

    def test_global_control_representative_values(self):

        # given
        model = TestModel.with_control_wells(
            {'001': ['A1', 'A2'], '002': ['A4']},
            None,
            {'001': ['C1', 'C2'], '002': ['C4']})

        # when
        actual = model.control_mask

        # then
        self.assertListEqual(self.get_mask(0, 1), list(actual[0, 0, 0]))
        self.assertListEqual(self.get_mask(3), list(actual[0, 0, 1]))

        self.assertListEqual(self.get_mask(), list(actual[1, 0, 0]))
        self.assertListEqual(self.get_mask(), list(actual[1, 0, 1]))

        self.assertListEqual(self.get_mask(24, 25), list(actual[2, 0, 0]))
        self.assertListEqual(self.get_mask(27), list(actual[2, 0, 1]))

    def test_local_control_representative_values(self):

        # given
        model = Model({
            'iterations': [
                {
                    'control': {
                        '001': ['A1', 'A2'],
                        '002': ['A4']
                    },
                    'spreadsheets': [
                        {
                            'filename': '',
                            'microplates': {
                                '001': {
                                    'values': []
                                },
                                '002': {
                                    'values': []
                                }
                            }
                        }
                    ]
                },
                {
                    'spreadsheets': [
                        {
                            'filename': '',
                            'microplates': {}
                        }
                    ]
                },
                {
                    'control': {
                        '001': ['C1','C2'],
                        '002': ['C4']
                    },
                    'spreadsheets': [
                        {
                            'filename': '',
                            'microplates': {
                                '001': {
                                    'values': []
                                },
                                '002': {
                                    'values': []
                                }
                            }
                        },
                        {
                            'filename': '',
                            'microplates': {
                                '001': {
                                    'values': []
                                },
                                '002': {
                                    'values': []
                                }
                            },
                            'control': {
                                '001': ['D12', 'H5'],
                                '002': ['F12', 'G6']
                            }
                        }
                    ]
                }
            ]
        })

        # when
        actual = model.control_mask

        # then
        self.assertListEqual(self.get_mask(0, 1), list(actual[0, 0, 0]))
        self.assertListEqual(self.get_mask(3), list(actual[0, 0, 1]))

        self.assertListEqual(self.get_mask(), list(actual[1, 0, 0]))
        self.assertListEqual(self.get_mask(), list(actual[1, 0, 1]))

        self.assertListEqual(self.get_mask(24, 25), list(actual[2, 0, 0]))
        self.assertListEqual(self.get_mask(27), list(actual[2, 0, 1]))

        self.assertListEqual(self.get_mask(24, 25, 47, 88), list(actual[2, 1, 0]))
        self.assertListEqual(self.get_mask(27, 71, 77), list(actual[2, 1, 1]))

    def test_api_equivalence(self):

        # given
        model = TestModel.with_control_wells(
            {'001': ['A1', 'A2'], '002': ['A4']},
            None,
            {'001': ['C1', 'C2'], '002': ['C4']})

        # when
        copy1 = model.control_mask(iteration=2, spreadsheet=0, microplate='001')
        copy2 = model.control_mask[2, 0, model.microplate_names().index('001')]

        # then
        self.assertListEqual(list(copy1), list(copy2))

    def get_mask(self, *args):

        mask = [False] * 96

        for i in args:
            mask[i] = True

        return mask


class TestSideEffect(unittest.TestCase):

    def test_no_side_effect_when_padding_missing_spreadsheets(self):

        # given
        json_data = {
            'iterations': [
                {
                    'spreadsheets': [
                        {
                            'filename': 'iteration1/spreadsheet1.xls',
                            'microplates': {
                                '001': {
                                    'values': [random() for i in xrange(96)]
                                },
                                '002': {
                                    'values': [random() for i in xrange(96)]
                                }
                            }
                        },
                        {
                            'filename': 'iteration1/spreadsheet2.xls',
                            'microplates': {
                                '001': {
                                    'values': [random() for i in xrange(96)]
                                },
                                '002': {
                                    'values': [random() for i in xrange(96)]
                                }
                            }
                        }
                    ]
                },
                {
                    'spreadsheets': [
                        {
                            'filename': 'iteration2/spreadsheet1.xls',
                            'microplates': {
                                '001': {
                                    'values': [random() for i in xrange(96)]
                                },
                                '002': {
                                    'values': [random() for i in xrange(96)]
                                }
                            }
                        }
                    ]
                }
            ]
        }

        # when
        model = Model(json_data)

        # then
        self.assertFalse(json_data is model.json_data)

        def num_spreadsheets(data, i):
            return len(data['iterations'][i]['spreadsheets'])

        self.assertEqual(num_spreadsheets(json_data, 0),
                         num_spreadsheets(model.json_data, 0))

        self.assertNotEqual(num_spreadsheets(json_data, 1),
                            num_spreadsheets(model.json_data, 1))


class TestModel(object):
    """Factory for microanalyst.model.Model instances."""

    @staticmethod
    def empty():
        return Model({'iterations': []})

    @staticmethod
    def with_filenames(*args):
        """Model with two iterations (2 spreadsheets and 1 spreadsheet):
           >>> TestModel.with_filenames(['foo', 'bar'], ['baz'])
        """

        iterations = []
        for filenames in args:
            iterations.append({
                'spreadsheets': [
                    {'filename': x, 'microplates': {}} for x in filenames
                ]
            })

        return Model({'iterations': iterations})

    @staticmethod
    def with_microplates(*args):
        """Model with two iterations and two spreadsheets each:
           >>> TestModel.with_microplates(
           >>>     [['001', '002'], ['001', '002']],
           >>>     [['003'], ['004']])
        """

        iterations = []
        for microplates in args:
            iterations.append({
                'spreadsheets': [
                    {
                        'filename': '',
                        'microplates': {y: {'values': []} for y in x}
                    } for x in microplates
                ]
            })

        return Model({'iterations': iterations})

    @staticmethod
    def with_genes(genes):
        """Model with one gene on well A1 of microplate 001:
           >>> TestModel.with_genes({'001':{'A1':'foobar'}})
        """
        return Model({'genes': genes, 'iterations': []})

    @staticmethod
    def with_random_values(*args):
        """Model with two iterations and two spreadsheets each:
           >>> TestModel.with_random_values(
           >>>     [['001', '002'], ['001', '002']],
           >>>     [['003'], ['004']])
        """

        def random_values():
            return {'values': [random() for i in xrange(96)]}

        iterations = []
        for i, microplates in enumerate(args):
            iterations.append({
                'spreadsheets': [
                    {
                        'filename': 'iteration%d/spreadsheet%d.xls' % (i+1, j+1),
                        'microplates': {y: random_values() for y in x}
                    } for j, x in enumerate(microplates)
                ]
            })

        return Model({'iterations': iterations})

    @staticmethod
    def with_control_wells(*args):
        """Model with three iterations (one spreadsheet each):
           >>> TestModel.with_control_wells(
                   {'001': ['A1', 'A2'], '002': ['A4']},
                   None,
                   {'001': ['C1', 'C2'], '002': ['C4']})
        """

        iterations = []
        for control_wells in args:

            if not control_wells:
                iterations.append({'spreadsheets': []})
            else:

                spreadsheets = [{
                    'filename': '',
                    'microplates': {
                        microplate: {
                            'values': []
                        } for microplate in control_wells
                    }
                }]

                iterations.append({
                    'control': control_wells,
                    'spreadsheets': spreadsheets
                })

        return Model({'iterations': iterations})
