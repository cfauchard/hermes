#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# hermes: __init__.py
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import sys
from hermes._version import __version__, __version_info__

__author__ = "Christophe Fauchard <christophe.fauchard@gmail.com>"

if sys.version_info < (3, 5):
    raise RuntimeError('You need Python 3.5+ for this module.')

from hermes.sftp import SFTPConnection
from hermes.ftp import FTPConnection
from hermes.exception import \
    ConnectionException, \
    AuthenticationException, \
    FileNotFoundException

__all__ = [ 'SFTPConnection',
            'FTPConnection',
            'ConnectionException',
            'AuthenticationException',
            'FileNotFoundException' ]
