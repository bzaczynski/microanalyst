#!/usr/bin/env python

from distutils.core import setup


def get_readme_content():
    with open('README') as file_handle:
        return file_handle.read()


setup(name='microanalyst',
      version='1.0.0',
      author='Bartosz Zaczynski',
      author_email='bartosz.zaczynski@gmail.com',
      url='https://bitbucket.org/bzaczynski/microanalyst',
      download_url='https://github.com/bzaczynski/microanalyst.git',
      description='Tecan(R) i-control(TM) Data Analysis',
      long_description=get_readme_content(),
      platforms = ['Any'],
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
      requires=[
          'xlwt',
          'xlrd',
          'numpy'
      ],
      packages=[
          'microanalyst',
          'microanalyst.commons',
          'microanalyst.gui',
          'microanalyst.model',
          'microanalyst.xls'
      ],
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
