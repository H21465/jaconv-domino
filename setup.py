# -*- coding: utf-8 -*-
from codecs import open
import os
import re
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'srcs', '__init__.py'), 'r', encoding='utf8') as f:
    version = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(f.read()).group(1)

setup(name='myjaconv',
      packages=['myjaconv'],
      version=version,
	  package_dir={'myjaconv': 'srcs'},
	  install_requires=[
			'setuptools',
			'wheel'
	  ],
      test_suite='nose.collector')