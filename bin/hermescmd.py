#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# hermes: hermescmd.py
#
# hermes command line tool
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import hermes
import zeus
import argparse
import re
import os
import shutil
import configparser
import paramiko

#
# global vars declaration
#
exclude_regex = None
include_regex = None
statuslogdir = None
statuslogdir_path = None
backupdir = None
backupdir_path = None

#
# download function
#
# parameters:
# - file_name: file name to download
#
def sftp_get_file(connection, file):

    date = zeus.date.Date()

    #
    # create status and backup dir
    #
    create_status_backup()

    #
    # download file
    #
    try:
        date.print()
        print("download", file, ": size", connection.get_size(file))
        connection.get(file, os.path.join(parser.get('hermes','localdir'), file))
    except:
        status = -1
    else:
        status = 0

        #
        # Backup downloaded file if transfer ok
        #
        print("backup file to", os.path.join(backupdir_path.path, file))
        shutil.copyfile(os.path.join(parser.get('hermes','localdir'), file),
                        os.path.join(backupdir_path.path, file))


#
# get command for sftp connection
#
def sftp_get(connection):

    print("command: get")

    #
    # List files in remote directory
    #
    list_files = connection.list()
    for file in list_files:

        #
        # test exclude regex
        #
        if exclude_regex and exclude_regex.match(file):
            print("WARNING: ", file, "excluded by excluderegex")

        #
        # test if directory
        #
        elif connection.is_dir(file):
            print("WARNING:", file, "directory excluded")

        #
        # test include regex
        #
        elif include_regex and not include_regex.match(file):
            print("WARNING:", file, "excluded by includeregex")

        #
        # download the file
        #
        else :
            sftp_get_file(connection, file)

#
# upload function
#
# parameters:
# - file_name: file path to upload
#
def sftp_put_file(connection, file):

    date = zeus.date.Date()

    #
    # create status and backup dir
    #
    create_status_backup()

    try:
        date.print()
        print("upload", file, ": size", os.path.getsize(file), "bytes")
        connection.put(file, os.path.basename(file))

    except:
        status = -1
    else:
        status = 0

        #
        # Backup uploaded file if transfer ok
        #
        print("backup file to", os.path.join(backupdir_path.path, os.path.basename(file)))
        shutil.copyfile(file,
                        os.path.join(backupdir_path.path, os.path.basename(file)))

    #
    # write statuslog file
    #
    if statuslogdir:
        print("writing in statuslogdir", os.path.join(statuslogdir_path.path, os.path.basename(file)), status)
        f = open(os.path.join(statuslogdir_path.path, os.path.basename(file)), 'w')
        date.update()
        f.write("%s;%s;%d;" % (date.date_time_iso(), file, status))
        f.close()

#
# command line parsing
#
args_parser = argparse.ArgumentParser()
args_parser.add_argument("--version", action='version', version='%(prog)s ' + hermes.__version__)
args_parser.add_argument("file", help="hermes config file")
args_parser.add_argument("--zkey", help="zeus secret key")
args = args_parser.parse_args()

try:

    #
    # display version and config informations
    #
    print("hermes version: " + hermes.__version__)
    print("zeus version: " + zeus.__version__)

    print("hermes config file: " + args.file)

    #
    # ZPK variable set with option in command line
    #
    if args.zkey is not None:
        os.environ["ZPK"] = args.zkey
        print("zeus key:", args.zkey)

    #
    # create an hermes connection object
    #
    connection = hermes.connection.Connection(args.file)

    print("connection to %s://%s@%s" % (connection.protocol, connection.user, connection.host))
    print("private key", connection.private_key)
    print("password", connection.crypted_password)
    print("connecting...", end='')
    connection.connect()
    print("ok")
    print("command", connection.command)
    connection.start()
    print("total:", connection.bytes_send, "bytes send,", connection.bytes_received, "bytes received")
    print("closing connection...", end='')
    connection.close()
    print("ok")
#
# exceptions tracking
#
except hermes.exception.AuthenticationException as error:
    print("ERROR: authentication exception", error.username, error.private_key)
    connection.last_connection(-1, "authentication exception")
except zeus.exception.InvalidConfigurationFileException as error:
    print("ERROR: invalid configuration file", error.filename)
except zeus.exception.PrivateKeyException:
    print("ERROR: ZPK variable for zeus key not set")
except hermes.exception.ActivationException:
    print("ERROR: activation set to no")
except hermes.exception.ProtocolUnsupportedException as error:
    print("ERROR: protocol unsupported", error.protocol)
except configparser.NoOptionError as error:
    print("ERROR missing key", error.option, "in section", error.section)
except hermes.exception.CommandUnsupportedException as error:
    print("ERROR unsupported command", error.command)
except hermes.exception.ChdirException as error:
    print("ERROR change directory", error.dir)
except zeus.exception.FileNotFoundException as error:
    print("ERROR file not found", error.filename)
except paramiko.ssh_exception.SSHException as error:
    print("ERROR sftp connexion", error.username)