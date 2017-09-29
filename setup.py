#!/usr/bin/env python3
# coding: utf8
# -----------------------------------------------------------------
# hermes: setup.py
#
# setup python package configuration
#
# Copyright (C) 2016-2017, Christophe Fauchard
# -----------------------------------------------------------------
from setuptools import setup
import os
import glob

exec(compile(open('hermes/_version.py').read(), 'hermes/_version.py', 'exec'))

setup(name='cfa_hermes',
      version=__version__,
      description='file tranfer monitor protocols ftp, sftp',
      url='https://github.com/cfauchard/hermes',
      author='Christophe Fauchard',
      author_email='christophe.fauchard@gmail.com',
      license='GPLV3',
      packages=['hermes'],
      scripts=['bin/hcmd.py', 'bin/hermesd.py'],
      data_files=[
            (
                  'sample/hermes', [
                        f for f in glob.glob(
                              os.path.join('sample', '*.hermes')
                        )
                  ]
            )
      ],
      install_requires=[
            'cfa_zeus >= 3.3.0.b1',
            'paramiko'
      ],
      zip_safe=False)
