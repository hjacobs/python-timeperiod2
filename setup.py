#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import os
from setuptools import setup

__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))

# Add here all kinds of additional classifiers as defined under
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
]


def read(fname):
    return open(os.path.join(__location__, fname)).read()

setup(name='timeperiod2',
      version='0.1',
      author='Henning Jacobs',
      author_email='henning.jacobs@zalando.de',
      description='Python module for determining if a datetime is within a time period',
      url='https://github.com/zalando/python-timeperiod2',
      py_modules=['timeperiod'],
      long_description=read('README.rst'),
      classifiers=CLASSIFIERS
      )
