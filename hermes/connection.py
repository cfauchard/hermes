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
