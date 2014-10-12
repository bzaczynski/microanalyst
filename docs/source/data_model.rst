.. _data-model:

Data Model
==========

Familiarity with data model used in microanalyst is central to understanding the usage of the tool. Virtually all information regarding an experiment is kept in a single `JSON <http://json.org/>`_ file acting as a container for hierarchical data. The reasons for choosing JSON over alternative file formats were the following:

* human readability
* portability
* compactness
* simplicity
* easily serieslized / deserieslized
* plain text rather than binary

The downside of using a text file instead of binary one is redundancy which makes the file grow rapidly in size. This can be mitigated by the choice of a more compact format such as YAML. However, benchmarks have shown that despite being about half the size of a similar JSON file the serialization of YAML takes an order of magnitude more time.

Schema
------

The structure of a document with experiment data as well as value constraints are formally defined by the follwing JSON schema. Scroll down for examples.
::
 {
     "$schema": "http://json-schema.org/schema#",
     "description": "Experiment data collected with microanalyst.",
     "definitions": {
         "control": {
             "description": "Control wells (defined statically per whole iteration or a particular spreadsheet within an iteration).",
             "type": "object",
             "additionalProperties": {
                 "description": "Microplate names, e.g. 001 or B002.",
                 "type": "array",
                 "maxItems": 96,
                 "items": {
                     "description": "Well addresses between A1 and H12.",
                     "type": "string",
                     "pattern": "^[A-H]([1-9]|10|11|12)$"
                 }
             }
         }
     },
     "type": "object",
     "required": ["iterations"],
     "properties": {
         "genes": {
             "description": "Genes used in the experiment.",
             "type": "object",
             "additionalProperties": {
                 "description": "Microplate names, e.g. 001 or B002.",
                 "type": "object",
                 "additionalProperties": false,
                 "patternProperties": {
                     "^[A-H]([1-9]|10|11|12)$": {
                         "description": "Well addresses between A1 and H12 mapped to gene names, e.g. YDL159W-A.",
                         "type": "string"
                     }
                 }
             }
         },
         "iterations": {
             "description": "An ordered list of consecutive experiment iterations.",
             "type": "array",
             "items": {
                 "description": "A single iteration comprising multiple spreadsheets, e.g. taken at 14-days intervals.",
                 "type": "object",
                 "required": ["spreadsheets"],
                 "properties": {
                     "control": {
                         "description": "Static control wells defined for all spreadsheets of this iteration.",
                         "$ref": "#/definitions/control"
                     },
                     "spreadsheets": {
                         "description": "An ordered list of metadata objects describing consecutive spreadsheets of this iteration.",
                         "type": "array",
                         "items": {
                             "description": "Metadata object with information about the original spreadsheet.",
                             "type": "object",
                             "required": ["filename", "microplates"],
                             "properties": {
                                 "control": {
                                     "description": "Additional control wells developed at a certain point in time in this spreadsheet.",
                                     "$ref": "#/definitions/control"
                                 },
                                 "filename": {
                                     "description": "Full name of the original Microsoft(R) Excel(TM) file.",
                                     "type": "string"
                                 },
                                 "microplates": {
                                     "description": "A set of microplates in this spreadsheet.",
                                     "type": "object",
                                     "additionalProperties": {
                                         "description": "Microplate names, e.g. 001 or B002.",
                                         "type": "object",
                                         "required": ["timestamp", "values"],
                                         "properties": {
                                             "temperature": {
                                                 "description": "Temperature at the time of the readout in Celsius degrees.",
                                                 "type": "number"
                                             },
                                             "timestamp": {
                                                 "description": "Date and time of the readout.",
                                                 "type": "string",
                                                 "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}$"
                                             },
                                             "values": {
                                                 "description": "An array of microplate values in row-major order.",
                                                 "type": "array",
                                                 "minItems": 96,
                                                 "maxItems": 96,
                                                 "items": {
                                                     "type": "number"
                                                 }
                                             }
                                         }
                                     }
                                 }
                             }
                         }
                     }
                 }
             }
         }
     }
 }

Root
^^^^

The root element is an object ``{}`` with ``iterations`` being the only mandatory child, while ``genes`` remain optional. Example::

 {
    "iterations": [],
    "genes": {},
 }

Genes
^^^^^

This is a global map of genes (proteins) scattered over microplates and their wells. It is assumed that this mapping remains consistent throughout the entire experiment and does not change in any of the iterations. The ``genes`` object maps microplates' names to wells' addresses (from A1 to H12). Then each well address is mapped to a gene name which can be an arbitrary text string. A microplate typically has only a subset of its wells assigned to genes. Example:

.. code-block:: javascript

 "genes": {
    "001": {
        "F5": "carotene"
        "A1": "collagen",
    },
    "007": {
        "G4": "myosin"
    }
 }

Control
^^^^^^^

There are specially designated wells on some microplates (determined by the manufacturer) that remain empty. This is to allow for validating optical density values of regular wells against noise such as infections. Control wells can be defined per iteration but also per a particular spreadsheet within an iteration. In both cases they are optional. Example:

.. code-block:: javascript

 "control": {
    "001" [
        "A1", "A2", "A3"
    ],
    "002": [
        "A1", "A2"
    ]
 }

Iterations
^^^^^^^^^^

This is an array ``[]`` of objects representing subsequent experiment series with Tecan® files and additional metadata described later. Note that the order of iterations must correspond to their actual sequence in time. Example:

.. code-block:: javascript

 "iterations": []

Iteration
^^^^^^^^^

An iteration is an anonymous object which must define ``spreadsheets`` array and may also define ``control`` wells property. Example::

 {
    "spreadsheets": [],
    "control": {}
 }

Spreadsheets
^^^^^^^^^^^^

This is an array ``[]`` of objects encapsulating key data from Tecan® files in chronological order. Example:

.. code-block:: javascript

 "spreadsheets": []

Spreadsheet
^^^^^^^^^^^

A spreadsheet is an anonymous object which must define ``filename`` (absolute path) corresponding to a Microsoft® Excel™ file and ``microplates`` object. It can also define additional ``control`` wells which will only become available in this particular spreadsheet. Example::

 {
    "filename": "C:\\experiment\\series2\\GAL_s02_21days.xls",
    "microplates": {},
    "control": {}
 }

Microplates
^^^^^^^^^^^

Microplates is an object ``{}`` whose keys are microplates' names. Example:

.. code-block:: javascript

 "microplates": {
    "001": {},
    "002": {}
 }

Microplate
^^^^^^^^^^

A microplate is an instance of a given microplate identified by its unique name and scanned at a particular point in time. It belongs to a spreadsheet within experiment series/iteration. It defines ISO 8601 ``timestamp``, Celsius degrees ``temperature`` and 96 floating point ``values``. Example:

.. code-block:: javascript

 "B002": {
    "timestamp": "2014-01-13T12:49:03",
    "temperature": 24.0,
    "values": [
        0.7184000015258789,
        0.6804999709129333,
        0.6837000250816345,
        (...)
    ]
 }