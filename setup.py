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

import os.path

from setuptools import setup, find_packages


def path(*parts):
    """Return an absolute path to the given resource."""
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, *parts)


def find_version():
    """Return the value of gpcommons.__version__."""
    with open(path('microanalyst', '__init__.py')) as fp:
        exec fp
    return locals().get('__version__')


setup(name=u'microanalyst',
      version=find_version(),
      author=u'Bartosz Zaczy\u0144ski',
      author_email=u'bartosz.zaczynski@gmail.com',
      url='https://github.com/bzaczynski/microanalyst',
      download_url='https://github.com/bzaczynski/microanalyst.git',
      description='Tecan(R) i-control(TM) Data Analysis',
      long_description=open(path('README.md')).read(),
      platforms=['Any'],
      keywords=['microbiology', 'microplate', 'microtiter', 'tecan'],
      license='MIT License',
      classifiers=(
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Visualization'
      ),
      dependency_links=[],
      install_requires=open(path('requirements.txt')).read().splitlines(),
      tests_require=[],
      test_suite='tests',
      packages=find_packages(exclude=['tests']),
      package_data={},
      scripts=[
          'scripts/group.py',
          'scripts/control.py',
          'scripts/genes.py',
          'scripts/assemble.py',
          'scripts/quantize.py',
          'scripts/xlsh.py',
          'scripts/xlsv.py',
          'scripts/manalyst.pyw'
      ])
