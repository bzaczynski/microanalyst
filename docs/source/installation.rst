Installation Instructions
=========================

Before commencing the analysis of data your work environment needs to be prepared. Depending on the platform and operating system these steps can vary slightly. Despite only Linux and Windows operating systems have been covered below a savvy Mac user should be able to follow without problems.

Python Interpreter
------------------

Microanalyst is distributed in the form of source code files intended to be executed by a Python interpreter. There are currently two major versions of the language, i.e. Python 2 and Python 3 which are largely incompatible. You want to make sure to be using the latest release of Python 2 which is going to be Python 2.7.x.

In addition to this a specific interpreter version may be available either for 32-bit or 64-bit computer architecture. However, it is recommended to choose the 32-bit one even on a 64-bit computer due to better availability of extension modules.

Linux
^^^^^

Chances are that Python is already installed. Otherwise use your distribution's package manager such as apt-get available on Debian/Ubuntu. ::

    $ sudo apt-get install python

Windows
^^^^^^^

Open your favorite web browser and navigate to `Python download page <http://www.python.org/download/>`_ for a list of available options. There is an easy to use Python installer which you can and should take advantage of. To check if Python has installed correctly open Windows command prompt and type *python* (e.g. press :kbd:`Windows + R`, then type *cmd* and confirm with :kbd:`Enter`)::

    C:\> python

You should be presented with something similar to this::

    Python 2.7.3 (default, Apr 10 2012, 23:24:47) [MSC v.1500 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

If that doesn't work it may be necessary to manually modify ``Path`` system variable in order to make ``python`` a recognizable command. On Windows 7 environment variables can be accessed by following these few steps:

    1. Right click *My Computer* icon and select *Properties*.
    2. Choose *Advanced system settings* from the menu on the left.
    3. Click *Environment variables...* button.
    4. Find system variable which says *Path* and double click it.
    5. Append a semicolon followed by the path to the Python interpreter.

By default Python installs under ``C:\Python27`` directory. Unless otherwise you should simply append ``;C:\Python27`` to the variable.

External Modules
----------------

Microanalyst depends on some external modules, e.g. for processing Microsoft® Excel™ files, which are not part of the standard Python installation. They need to be installed manually, namely:

    * ``xlrd`` for reading .xls files
    * ``xlwt`` for writing .xls files
    * ``NumPy`` for scientific computing

The easiest way of adding modules and packages to Python is with a package manager such as *easy_install* (which is a part of `setuptools <https://pypi.python.org/pypi/setuptools>`_) or *pip*. Unfortunately Python comes with none of them by default so a package manager needs to be installed before.

Linux
^^^^^

On Linux certain popular Python modules may be available directly through system's package manager like apt-get, e.g.::

    $ sudo apt-get install python-xlrd python-xlwt python-numpy

Windows
^^^^^^^

The recommended way of installing easy_install on Windows is by downloading and executing `ez_setup.py <https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py>`_ script from the `setuptools <https://pypi.python.org/pypi/setuptools>`_ page. Afterwards, the ``Path`` system variable must be modified again. This time with a path to the ``Scripts`` subfolder::

    ;C:\Python27\Scripts

.. hint::
   To improve maintainability one can create a custom system variable (e.g. called ``PYTHON_PATH``) with all paths related to Python and refer to it in the ``Path`` variable instead of using literals, e.g.::

     PYTHON_PATH=C:\Python27;C:\Python27\Scripts
     Path=(...);%PYTHON_PATH%

Finally, to install the required modules::

    C:\> easy_install xlrd xlwt numpy

Alternatively one can try an unofficial module installer provided by a 3rd party such as the one `here <http://www.lfd.uci.edu/~gohlke/pythonlibs/#setuptools>`_. Some external Python modules are only distributed in source form and require a number of additional tools for compilation, which is a hassle particularly on Windows. Precompiled binary distributions of such modules are much easier to install on the other hand.

Installing microanalyst
-----------------------

Microanalyst is comprised of a Python module under the same name as well as a number of scripts which are built on top of it. To install microanalyst follow the standard procedure and type this command (works the same way on Windows and Linux, though root/sudo access may be needed for the latter)::

    C:\> cd microanalyst
    C:\microanalyst> python setup.py install

Testing the Installation
------------------------

To verify if the installation was successful you can exercise a comprehensive unit test suite. Change directory to ``test/`` subfolder and use the test discovery feature as shown below::

    C:\microanalyst> cd test
    C:\microanalyst\test> python -m unittest discover -v

Generating Documentation
------------------------

The following document can be generated automatically with the `Sphinx <http://sphinx-doc.org/>`_ tool.

Linux
^^^^^

Ensure that ``make`` and ``python-sphinx`` are installed, then follow these steps to build the documentation::

    $ cd microanalyst/doc
    $ make html

Windows
^^^^^^^

Install Sphinx first::

    C:\> easy_install sphinx


Use the ``sphinx-build`` command to generate documentation and place it under ``build`` folder::

    C:\> cd microanalyst\doc
    C:\microanalyst\doc> sphinx-build source build
