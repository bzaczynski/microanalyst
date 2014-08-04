Introduction
============

About
-----

Microanalyst is both a Python module and a set of utility scripts for the analysis and visualization of data acquired with Tecan® i-control™ microplate reader.

Motivation
----------

The original experiment which led to the inception of this project was held at the `Institute of Environmental Sciences <http://www.eko.uj.edu.pl/index.php/en/>`_ of the `Jagiellonian University <http://www.uj.edu.pl/en_GB/>`_.

The goal of the experiment was to determine genes whose expression gives a strong effect on survival of non-dividing cells in a repeatable manner.

There were around 6,000 yeast strains (*Saccharomyces cerevisiae*) with different sets of genes. Yeast extinction and survival would be observed by keeping the samples in a carbon-free environment. The entire collection of 65 microplates (8 rows by 12 columns each) was measured at roughly two-weeks time intervals and repeated in a few redundant series.

Microplates
^^^^^^^^^^^

* There were 65 microplates in the whole experiment.
* Each microplate had a unique name.
* Each microplate consisted of 96 wells with samples.
* Wells were arranged in 8 rows denoted with letters [A-H] and 12 columns denoted with numbers [1-12].
* Some microplates did contain empty control wells, whose presence and location had been determined by the manufacturer upfront.

Spreadsheets
^^^^^^^^^^^^

* Microplates were scanned with a Tecan® Infinite® 200 reader device, which produced .xls files (Microsoft® Excel™).
* A single Excel™ document could contain readouts taken over a period of multiple days, although typically there would be a one-to-one relationship, i.e. one Excel™ file per day.
* It took approximately 40 seconds to scan one microplate.
* The readout of a single microplate included the following:

  * name of the microplate
  * date and time
  * temperature in Celsius degrees (usually around 30 degrees)
  * 96 floating point values (e.g. associated with the absorbance - optical density - at a particular wavelength and bandwidth)

* Name of an Excel™ sheet coincided with the corresponding microplate name.
* Additional sheets with metadata were ignored.
* Excel™ sheets were stored in no particular order.

Interpretation
^^^^^^^^^^^^^^

* Values below 0.2 were considered starvation of a sample.
* Values above 0.8 were most likely an unwanted infection.
* Values above 0.06 in a control well also indicated a high probability of an infection in the microplate since that is the absorbance of the material comprising the microplates.