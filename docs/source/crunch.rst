Data Crunching
==============

Load Experiment
---------------

Standalone Mode
^^^^^^^^^^^^^^^

To interactively inspect and manipulate experiment data in standalone mode::

  C:\> python -m microanalyst experiment.json
  Type "model", "help(model)" for more information.
  >>>

This opens Python console with preloaded instance of the model to run queries on. Type ``help(model)`` for details or take a look at the unit tests which go into much greater detail with respect to possible use cases compared to the examples below.

Import
^^^^^^

Using microanalyst as a module, e.g. in a custom script or from `IPython <http://ipython.org>`_ Notebook which is a popular tool among the scientific community::

 >>> import microanalyst.model
 >>> model = microanalyst.model.from_file(r'C:\data\experiment.json')

Query Examples
--------------

Well Names
^^^^^^^^^^

A static list of 96 well names on an 8x12 microplate in row-major order (returns a generator object)::

 >>> for i, name in enumerate(model.well_names()):
 >>>     print '[%d] = %s' % (i, name)
 [0] = A1
 [1] = A2
 [2] = A3
 (...)

Microplate Names
^^^^^^^^^^^^^^^^

Microplates used in the whole experiment::

 >>> model.microplate_names()
 [u'001', u'002', u'003', (...), u'B001', u'B002']

To restrict the lookup domain use one or both of the indices: ``spreadsheet``, ``iteration``::

 >>> model.microplate_names(spreadsheet=0)
 [u'001', u'002', u'003', (...), u'B001', u'B002']

Genes/Proteins
^^^^^^^^^^^^^^

Return a sorted list of unique genes::

 >>> model.genes()
 ['ART2', 'HMLALPHA2', 'Q0017', 'Q0080', 'Q0085', (...)]

To obtain a list of genes actually used in the experiment, i.e. the ones that are mapped to existing microplates call ``genes_used()``::

 >>> a = set(model.genes())
 >>> b = set(model.genes_used())
 >>> c = a.difference(b)
 >>> len(a), len(b), len(c)
 (5869, 5590, 279)

Genes can be restricted to a given microplate, well or both. The ``microplate`` argument is the name of a microplate such as "B002" while ``well`` can be either a 0-based index or a string such as "H12". For example to get all genes on a certain microplate::

 >>> model.genes(microplate='B002')
 ['YBL097W', 'YBR004C', 'YBR021W', 'YBR174C', (...)]

Getting a single gene rather than an array is done with a ``gene_at()`` method which expects both arguments::

 >>> model.gene_at(microplate='B002', well='E8')
 'YBL097W'

Alternatively to obtain a gene by its name (case insensitive)::

 >>> model.gene('ybl097w')
 'YBL097W'

Genes shown in previous examples are not just textual names but fully-fledged objects encapsulating useful information::

 >>> for gene in model.genes():
 >>>     info = (gene.name, gene.microplate_name, gene.well_name)
 >>>     print 'Gene "%s" is located on microplate "%s" at well "%s".' % info
 >>>
 Gene "ART2" is located on microplate "025" at well "D2".
 Gene "HMLALPHA2" is located on microplate "053" at well "E9".
 Gene "Q0017" is located on microplate "001" at well "D6".
 (...)

.. note::
    It is assumed that genes are bijectively mapped to (microplate, well) pairs. If a gene occurs more than once, i.e. duplicates are found on one or more microplates, this may lead to undefined and faulty results. Textual warnings are issued for duplicate instances of genes.

Instances of genes are also callable function objects::

 >>> for gene in model.genes():
 >>>     print gene, gene()
 ART2 (u'025', u'D2')
 HMLALPHA2 (u'053', u'E9')
 Q0017 (u'001', u'D6')
 (...)

Finally, they can be used to quickly obtain corresponding data samples with a convenience method which is a wrapper over model's ``values()``. By default all experiment iterations and spreadsheets are taken into account but this can be restricted with two optional parameters, i.e. ``iteration`` and ``spreadsheet`` (both are 0-based indices). Example::

 >>> for gene in model.genes_used():
 >>>     print gene.values().ravel()
 [0.6780999898910522, 0.6870999932289124, 0.6870999932289124, (...)]
 [0.633899986743927, 0.7077000141143799, 0.679099977016449, (...)]
 (...)

Well Values
^^^^^^^^^^^

Due to large amounts of numerical data in the experiment `NumPy <http://www.numpy.org>`_ is a natural choice for storage and computation. Data samples are kept in a non-jagged 4-dimensional floating-point array where consecutive dimentions are: ``iteration`` x ``spreadsheet`` x ``microplate`` x ``well``. To take full advantage of speed improvements over Python's lists each dimension is ensured to contain subarrays of the same size. This is achieved by padding missing spreadsheets if necessary (the remaining dimensions do not matter, e.g. a microplate is always assumed to have 96 wells).

The array can be manipulated directly leveraging NumPy features by accessing ``array4d`` property, e.g.::

 >>> model.array4d.shape
 (3, 4, 65, 96)

However, a pivotal way for slicing the array is through the ``values()`` method which uses explicitly named arguments (all are optional). Additionally ``microplate`` and ``well`` can be either 0-based indices or names. Missing values are indicated with ``None``. The rows in this case correspond to iterations, whereas the columns to Excel™ spreadsheets::

 >>> model.values(microplate='001', well='A1')
 array([[ 0.7385    ,  0.66869998,  0.66420001],
        [ 0.74629998,  0.70660001,  0.63870001],
        [ 0.71689999,  0.78380001,  0.72259998]])

Control Wells
^^^^^^^^^^^^^

To explicitly check if a particular well is a control well (either names or 0-based indices can be used for both ``microplate`` and ``well`` arguments)::

 >>> model.is_control(iteration=0, spreadsheet=0, microplate='008', well='A4')
 True

There is also a mask for quick retrieval of control wells which can be used to eliminate them from the whole experiment at once. For instance clamping starved samples can be done like that::

 >>> model.array4d[(model.array4d <= 0.2) & ~model.control_mask.values] = 0.0

.. note::

    Gaps in data samples may cause discrepancies in the total number of control wells reported. Missing microplates are not accounted for when using ``control_mask`` or when iterating over array dimensions, e.g.::

     >>> len(model.array4d[model.control_mask.values])
     2056
     >>>
     >>> max_i, max_s, max_m, max_w = model.array4d.shape
     >>> num_control = 0
     >>> for i in xrange(max_i):
     >>>     for s in xrange(max_s):
     >>>         for m in xrange(max_m):
     >>>             for w in xrange(max_w):
     >>>                 if model.is_control(i, s, m, w):
     >>>                     num_control += 1
     >>> num_control
     2056

    To obtain an actual number of control wells, i.e. without missing data samples, iterate over raw JSON::

     >>> from microanalyst.model import welladdr
     >>>
     >>> num_control = 0
     >>> for i, iteration in enumerate(model.json_data['iterations']):
     >>>     for s, spreadsheet in enumerate(iteration['spreadsheets']):
     >>>         for m in spreadsheet['microplates']:
     >>>             for w in welladdr.names():
     >>>                 if model.is_control(i, s, m, w):
     >>>                     num_control += 1
     >>> num_control
     2042

File names
^^^^^^^^^^

Return a flat list of file names used throughout the experiment::

 >>> from pprint import pprint
 >>> pprint(model.filenames())
 [u'/home/microanalyst/experiment/series1/series1_14days.xls',
  u'/home/microanalyst/experiment/series1/series1_28days.xls',
  u'/home/microanalyst/experiment/series1/series1_42days.xls',
  u'/home/microanalyst/experiment/series1/series1_56days.xls',
  u'/home/microanalyst/experiment/series2/series2_14days.xls',
  u'/home/microanalyst/experiment/series2/series2_28days.xls',
  u'/home/microanalyst/experiment/series2/series2_42days.xls',
  u'/home/microanalyst/experiment/series2/series2_56days.xls',
  u'/home/microanalyst/experiment/series3/series3_14days.xls',
  u'/home/microanalyst/experiment/series3/series3_28days.xls',
  u'/home/microanalyst/experiment/series3/series3_42days.xls',
  u'/home/microanalyst/experiment/series3/series3_56days.xls']

Restrict to only the second iteration and hide paths::

 >>> pprint(model.filenames(False, iteration=1))
 [u'series2_14days.xls',
  u'series2_28days.xls',
  u'series2_42days.xls',
  u'series2_56days.xls']

Number of Experiment Iterations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

 >>> model.num_iter
 3

Parsed JSON Data
^^^^^^^^^^^^^^^^

If the underlying model does not live up to your needs you can retrieve a Python dictionary built from raw JSON and process it in any way you can possibly imagine. This may be handy for accessing ignored metadata such as custom annotations (e.g. introduced with ``group.py`` script). Example::

 >>> temperatures = []
 >>> for iteration in model.json_data['iterations']:
 >>>     for spreadsheet in iteration['spreadsheets']:
 >>>         for microplate in spreadsheet['microplates'].values():
 >>>             temperatures.append(microplate['temperature'])
 >>>
 >>> print 'Average temperature was %.1f Celsius' % (sum(temperatures) / float(len(temperatures)))
 Average temperature was 27.5 Celsius

A deep copy of the original JSON is created to avoid side effects, e.g. when missing spreadsheets are substituted with empty stubs. If that hapens an appropriate warning message is printed to the console.
