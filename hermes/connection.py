#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# hermes: connection.py
#
# Define generic hermes connection class
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import zeus
import hermes
import re
import os

class Connection:

    def __init__(self, hermes_config_file):

        #
        # create an ini file parser
        #
        self.parser = zeus.parser.ConfigParser(hermes_config_file)

        #
        # raise an ActivationException if activation = no
        #
        if not self.parser.get('hermes', 'activation') == 'yes':
            print(self.parser.get('hermes', 'activation'))
            raise hermes.exception.ActivationException()

        self.commands = { 'get': self.get, 'put': self.put }
        self.bytes_send = 0
        self.bytes_received = 0

        #
        # create working directories
        #
        self.create_backup_dir()
        self.create_status_dir()

        #
        # getting mandatory parameters
        #
        self.host = self.parser.get('hermes', 'host')
        self.user = self.parser.get('hermes', 'user')
        self.localdir = self.parser.get('hermes', 'localdir')
        zeus.file.Path(self.localdir)
        self.remotedir = self.parser.get('hermes', 'remotedir')
        self.command = self.parser.get('hermes', 'command')
        if self.parser.get('hermes', 'protocol') == "sftp":
            self.protocol = "sftp"
        else:
            raise hermes.exception.ProtocolUnsupportedException(self.parser.get('hermes', 'protocol'))

        #
        # getting optional parameters
        #
        if (self.parser.has_option('hermes', 'private_key')):
            self.private_key = self.parser.get('hermes', 'private_key')
            self.password = None
            self.crypted_password = None
        elif (self.parser.has_option('hermes', 'cryptedpassword')):
            self.crypted_password = self.parser.get('hermes', 'cryptedpassword')
            self.cipher = zeus.crypto.Vigenere()
            self.cipher.decrypt(self.crypted_password)
            self.password = self.cipher.get_decrypted_datas_utf8()
            self.private_key = None

        #
        # regex compilation
        #
        if self.parser.has_option('hermes', 'excluderegex'):
            self.exclude_regex = re.compile(self.parser.get('hermes', 'excluderegex'))
        else:
            self.exclude_regex = None

        if self.parser.has_option('hermes', 'includeregex'):
            self.include_regex = re.compile(self.parser.get('hermes', 'includeregex'))
        else:
            self.include_regex = None

    def connect(self):

        #
        # SFTP protocol
        #
        if self.protocol == "sftp":

            #
            # create an hermes.SFTPConnection object with private key
            #
            if self.private_key is not None:
                self.protocol_connection = hermes.sftp.SFTPConnection(
                    self.host,
                    self.user,
                    private_key = self.private_key)

            #
            # create an hermes.SFTPConnection object with login/password
            #
            elif self.password is not None:
                self.protocol_connection = hermes.sftp.SFTPConnection(
                    self.host,
                    self.user,
                    password = self.password)

        #
        # chdir to remote directory
        #
        self.protocol_connection.chdir(self.remotedir)

    def close(self):
        self.protocol_connection.close()

    def create_status_dir(self):

        #
        # create statuslog dir if it does not exist
        #
        date = zeus.date.Date()
        if (self.parser.get('hermes', 'statuslogdir')):
            self.statuslogdir = self.parser.get('hermes', 'statuslogdir')
            self.statuslogdir_path = zeus.file.Path(date.path_date_tree(self.statuslogdir))

    def create_backup_dir(self):

        #
        # create backupdir if it does not exists
        #
        date = zeus.date.Date()
        if (self.parser.get('hermes', 'backupdir')):
            self.backupdir = self.parser.get('hermes', 'backupdir')
            self.backupdir_path = zeus.file.Path(date.path_date_tree(self.backupdir))

    def get(self, callback = None):
        print("exec get")

    def put(self, callback = None):

        #
        # List files in local directory
        #
        for file in os.listdir(self.localdir):
            callback(os.path.join(self.localdir, file),
                     os.path.getsize(os.path.join(self.localdir, file)))

            self.bytes_send += os.path.getsize(os.path.join(self.localdir, file))

    def start(self, callback = None):
        try:
            self.commands[self.command](callback)
        except KeyError:
            raise hermes.exception.CommandUnsupportedException(self.command)