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
import shutil

def default_callback(connection, file, size, status):
    connection.log.logger.info("%s %d bytes : %s",
                               file,
                               size,
                               status)

class Connection:

    def __init__(self, hermes_config_file):

        #
        # create an ini file parser and read config file
        #
        self.parser = zeus.parser.ConfigParser(hermes_config_file)

        #
        # logfile
        #
        if self.parser.has_option('hermes', 'logfile'):

            #
            # create 512Ko switch log
            #
            self.log = zeus.log.Log(
                self.parser.get('hermes', 'logfile'),
                size=1024 * 512
            )
        else:

            #
            # create an stdout only logger
            #
            self.log = zeus.log.Log()

        self.log.logger.info("initializing Hermes Connection whith %s", hermes_config_file)
        self.log.logger.info("hermes %s", hermes.__version__)
        self.log.logger.info("zeus %s", zeus.__version__)

        #
        # raise an ActivationException if activation = no
        #
        if not self.parser.get('hermes', 'activation') == 'yes':
            self.log.logger.warning("not activated")
            raise hermes.exception.ActivationException()

        #
        # intern variables initialization
        #
        self.commands = {'get': self.get, 'put': self.put}
        self.bytes_send = 0
        self.bytes_received = 0
        self.status = None
        self.last_transfer = None
        self.last_transfer_size = 0

        #
        # create working directories
        #
        if self.parser.has_option('hermes', 'backupdir'):
            self.backupdir_base = self.parser.get('hermes', 'backupdir')
            self.backupdir = zeus.file.DayArchivePath(self.backupdir_base)
            self.log.logger.info("backupdir %s created", self.backupdir.path)
        else:
            self.backupdir = None
            self.log.logger.info("no backupdir")
        if self.parser.has_option('hermes', 'statuslogdir'):
            self.statuslogdir_base = self. parser.get('hermes', 'statuslogdir')
            self.statuslogdir = zeus.file.DayArchivePath(self.statuslogdir_base)
            self.log.logger.info("statuslogdir %s created", self.statuslogdir.path)
        else:
            self.statuslogdir = None
            self.log.logger.info("no statuslogdir")

        #
        # getting mandatory parameters
        #
        self.host = self.parser.get('hermes', 'host')
        self.user = self.parser.get('hermes', 'user')
        self.localdir = self.parser.get('hermes', 'localdir')
        zeus.file.Path(self.localdir)
        self.remotedir = self.parser.get('hermes', 'remotedir')
        self.command = self.parser.get('hermes', 'command')
        self.deleteflag = self.parser.get('hermes', 'deleteflag')
        if self.parser.get('hermes', 'protocol') == "sftp":
            self.protocol = "sftp"
        else:
            raise hermes.exception.ProtocolUnsupportedException(self.parser.get('hermes', 'protocol'))

        #
        # display mandatory parameters
        #
        self.log.logger.info("host %s", self.host)
        self.log.logger.info("user %s", self.user)
        self.log.logger.info("localdir %s", self.localdir)
        self.log.logger.info("remotedir %s", self.remotedir)
        self.log.logger.info("command %s", self.command)
        self.log.logger.info("deleteflag %s", self.deleteflag)
        self.log.logger.info("protocol %s", self.protocol)

        #
        # Getting optionnal parameters
        #
        if self.parser.has_option('hermes', 'port'):
            self.port = int(self.parser.get('hermes', 'port'))
            self.log.logger.info("port %d", self.port)

        #
        # authentication options
        #
        if self.parser.has_option('hermes', 'private_key'):
            self.private_key = self.parser.get('hermes', 'private_key')
            self.password = None
            self.crypted_password = None
            self.log.logger.info("private key authentication %s", self.private_key)
        elif (self.parser.has_option('hermes', 'cryptedpassword')):
            self.crypted_password = self.parser.get('hermes', 'cryptedpassword')
            self.cipher = zeus.crypto.Vigenere()
            self.cipher.decrypt(self.crypted_password)
            self.password = self.cipher.get_decrypted_datas_utf8()
            self.private_key = None
            self.log.logger.info("password authentication %s", self.crypted_password)
            self.log.logger.info("zeus encryption key %s", os.environ["ZPK"])


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

    def write_last_connection(self, status, libelle):
        f = open(os.path.join(self.statuslogdir_base,"last_connection"), 'w')
        f.write("%s,%d,%s" % (zeus.date.Date().date_time_iso(), status, libelle))
        f.close()

    def connect(self):

        #
        # SFTP protocol
        #
        if self.protocol == "sftp":

            #
            # create an hermes.SFTPConnection object with private key authentication
            #
            if self.private_key is not None:
                self.protocol_connection = hermes.sftp.SFTPConnection(
                    self.host,
                    self.user,
                    port=self.port,
                    private_key=self.private_key)

            #
            # create an hermes.SFTPConnection object with login/password authentication
            #
            elif self.password is not None:
                self.protocol_connection = hermes.sftp.SFTPConnection(
                    self.host,
                    self.user,
                    port=self.port,
                    password=self.password)

        #
        # chdir to remote directory
        #
        self.protocol_connection.chdir(self.remotedir)

        #
        # update last connection
        #
        self.write_last_connection(0, "no error")

    def close(self):
        self.protocol_connection.close()


    #
    # write statuslog file
    #
    def write_status(self, file):

        if self.statuslogdir is not None:
            date = zeus.date.Date()

            self.log.logger.info("writing in statuslogdir %s %s",
                                 os.path.join(self.statuslogdir.path, os.path.basename(file)),
                                 self.status)
            f = open(os.path.join(self.statuslogdir.path, os.path.basename(file)) + ".idx", 'w')
            f.write("%s,%d,%s,%d,%s" % (os.path.join(self.localdir, os.path.basename(file)),
                                        self.last_transfer_size,
                                        date.date_time_iso(),
                                        self.statuscode,
                                        self.status))
            f.close()

    def write_backup(self, file):

        if self.backupdir is not None:
            self.log.logger.info("backup file %s to %s",
                                    file,
                                    os.path.join(self.backupdir.path, os.path.basename(file)))
            shutil.copyfile(file,
                            os.path.join(self.backupdir.path, os.path.basename(file)))

    def get_file(self, file):

        self.last_transfer = file
        try:
            self.protocol_connection.get(file, os.path.join(self.localdir, file + ".tmp"))
            self.log.logger.info("local rename %s to %s",
                            os.path.join(self.localdir, file + ".tmp"),
                            os.path.join(self.localdir, file))
            os.rename(os.path.join(self.localdir, file + ".tmp"), os.path.join(self.localdir, file))
            self.last_transfer_size = os.path.getsize(os.path.join(self.localdir, file))
            self.bytes_received += self.last_transfer_size

            #
            # Backup uploaded file if transfer ok
            #
            self.write_backup(os.path.join(self.localdir, file))

            #
            # delete the local file
            #
            if self.deleteflag == "yes":
                self.protocol_connection.remove(file)
                self.status = "downloaded and remote deleted"
            else:
                self.status = "downloaded"

            self.statuscode = 0

        except PermissionError as error:
            self.status = "permission denied"
            self.statuscode = -2
        except:
            self.log.logger.warn("unknown error catched")
            self.status = "unknown error"
            self.statuscode = -1

        self.write_status(file)

    def get(self, callback):
        for file in self.protocol_connection.list():

            #
            # exclude directories
            #
            if self.protocol_connection.is_dir(file):
                self.status = "excluded (directory)"

            #
            # test exclude regex
            #
            elif self.exclude_regex and self.exclude_regex.search(file):
                self.status = "excluded by excluderegex"

            #
            # test include regex
            #
            elif self.include_regex and not self.include_regex.search(file):
                self.status = "excluded by includeregex"

            #
            # download the file
            #
            else:
                self.get_file(file)

            #
            # callback function
            #
            if not callback == None:
                callback(self,
                         file,
                         self.last_transfer_size,
                         self.status)

        self.log.logger.info("total received: %d bytes", self.bytes_received)

    def put(self, callback):

        #
        # List files in local directory
        #
        for file in os.listdir(self.localdir):

            #
            # exclude directories
            #
            if os.path.isdir(os.path.join(self.localdir, file)):
                self.status = "excluded (directory)"

            #
            # test exclude regex
            #
            elif self.exclude_regex and self.exclude_regex.search(file):
                self.status = "excluded by excluderegex"

            #
            # test include regex
            #
            elif self.include_regex and not self.include_regex.search(file):
                self.status = "excluded by includeregex"

            #
            # upload the file
            #
            else:
                self.put_file(os.path.join(self.localdir, file))

            #
            # callback function
            #
            if not callback == None:
                callback(self,
                         file,
                         self.last_transfer_size,
                         self.status)

        self.log.logger.info("total sent: %d bytes", self.bytes_send)


    def put_file(self, file):
        self.last_transfer = file
        try:
            self.protocol_connection.put(file, os.path.basename(file + ".tmp"))
            self.log.logger.info("remote rename %s to %s",
                                 os.path.basename(file + ".tmp"),
                                 os.path.basename(file))
            self.protocol_connection.rename(os.path.basename(file + ".tmp"),
                                            os.path.basename(file))
            self.last_transfer_size = os.path.getsize(file)
            self.bytes_send += self.last_transfer_size

            #
            # Backup uploaded file if transfer ok
            #
            self.write_backup(file)

            #
            # delete the local file
            #
            if self.deleteflag == "yes":
                os.remove(file)
                self.status = "uploaded and local deleted"
            else:
                self.status = "uploaded"

            self.statuscode = 0

        except PermissionError as error:
            self.status = "permission denied"
            self.statuscode = -2
        # except:
        #     self.log.logger.warn("unknown error catched")
        #     self.status = "unknown error"
        #     self.statuscode = -1

        self.write_status(file)

    def start(self, callback=default_callback):
        try:
            self.commands[self.command](callback)
        except KeyError:
            raise hermes.exception.CommandUnsupportedException(self.command)

