# [micro&middot;analyst](https://github.com/bzaczynski/microanalyst)

Microanalyst is a set of Python scripts for the analysis and visualization of data acquired with Tecan&reg; i-control&trade; microplate reader.

### Installation

1. Download and install Python modules for Microsoft&reg; Excel&trade; processing and scientific computing:

        $ pip install xlrd xlwt numpy

    or

        $ easy_install xlrd xlwt numpy

2. Download and install microanalyst module along with helper scripts:

        $ git clone https://github.com/bzaczynski/microanalyst
        $ cd microanalyst
        $ python setup.py install

### Usage

Refer to [documentation](https://readthedocs.org/projects/microanalyst) for details.


### Unit Testing

    $ cd microanalyst/test
    $ python -m unittest discover

### Contact

* Bartosz Zaczyński - program author - <bartosz.zaczynski@gmail.com>
* Elżbieta Pogoda - researcher - <elzbieta.pogoda1@gmail.com>

### License

This project is licensed under the [MIT License](https://raw.githubusercontent.com/bzaczynski/microanalyst/master/LICENSE).
