##
## Copyright 2024 Zest AI All Rights Reserved
##
##
##
## It is prohibited to copy, in whole or in part, modify, directly or indirectly reverse engineer, disassemble, decompile, decode or adapt this code or any portion or aspect thereof, or otherwise attempt to derive or gain access to any part of the source code or algorithms contained herein as provided in your ZAML agreement.
##
import os
from setuptools import setup, find_packages
from pathlib import Path

with open('requirements.txt') as fp:
    REQUIRED = fp.read()
MODULE_NAME = "ztestdata"
current_directory = Path(__file__).parent
VERSION_FILE = current_directory / MODULE_NAME / ".VERSION"
with open(VERSION_FILE) as f:
    __version__ = f.read().strip()

setup(name='ztestdata',
      version=__version__,
      description='Zest Automated Machine Learning tool set',
      url='https://github.com/Katlean/ztestdata',
      author='ZestAI Data Science Team',
      author_email='core-modeling@zestfinance.com',
      packages=find_packages(),
      install_requires=REQUIRED,
      python_requires='>=3.7',
      zip_safe=False,
      include_package_data=True
      )