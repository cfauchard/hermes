#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# hermes: exception.py
#
# Define hermes exception handler
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

class ConnectionException(Exception):

    def __init__(self, host, port):
        self.host = host
        self.port = port

class AuthenticationException(Exception):

    def __init__(self, username, private_key=None):
        self.username = username
        self.private_key = private_key

class FileNotFoundException(Exception):

    def __init__(self, filename):
        self.filename = filename
        