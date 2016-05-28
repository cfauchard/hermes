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
    # write statuslog file
    #
    if statuslogdir:
        print("writing in statuslogdir", os.path.join(statuslogdir_path.path, file), status)
        f = open(os.path.join(statuslogdir_path.path, file), 'w')
        date.update()
        f.write("%s;%s;%d;" % (date.date_time_iso(), os.path.join(parser.get('hermes','localdir'), file), status))
        f.close()

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
# put command for sftp connection
#
def sftp_put(connection):
    print("command: put")

    #
    # List files in local directory
    #
    for file in os.listdir(parser.get('hermes','localdir')):

        #
        # exclude directories
        #
        if os.path.isdir(file):
            print("WARNING: ", file, "directory excluded")

        #
        # test exclude regex
        #
        elif exclude_regex and exclude_regex.match(file):
            print("WARNING: ", file, "excluded by excluderegex")

        #
        # test include regex
        #
        elif include_regex and not include_regex.match(file):
            print("WARNING: ", file, "excluded by includeregex")

        #
        # upload the file
        #
        else:
            sftp_put_file(connection, os.path.join(parser.get('hermes','localdir'), file))


#
# SFTP protocol
#
def sftp():
    print("sftp protocol")

    print("sftp connexion to",
          parser.get('hermes', 'user') + "@" + parser.get('hermes', 'host'))

    #
    # create an hermes.SFTPConnection object with private key
    #
    if (parser.has_option('hermes', 'private_key')):
        print("private key authentication",
          parser.get('hermes', 'private_key'),
          "..."
          )

        connection = hermes.sftp.SFTPConnection(
            parser.get('hermes', 'host'),
            parser.get('hermes', 'user'),
            private_key = parser.get('hermes', 'private_key'))
        print("sftp connexion opened...OK")


    #
    # create an hermes.SFTPConnection object with login/password
    #
    elif (parser.has_option('hermes', 'cryptedpassword')):
        print("password authentication")
        crypted_password = parser.get('hermes', 'cryptedpassword')
        print("crypted password:", crypted_password)
        cipher = zeus.crypto.Vigenere()
        cipher.decrypt(crypted_password)
        password = cipher.get_decrypted_datas_utf8()

        connection = hermes.sftp.SFTPConnection(
            parser.get('hermes', 'host'),
            parser.get('hermes', 'user'),
            password = password)
        print("sftp connexion opened...OK")

    #
    # regex compilation
    #
    if parser.has_option('hermes', 'excluderegex'):
        exclude_regex = re.compile(parser.get('hermes', 'excluderegex'))
    else:
        exclude_regex = None

    if parser.has_option('hermes', 'includeregex'):
        include_regex = re.compile(parser.get('hermes', 'includeregex'))
    else:
        include_regex = None

    #
    # change local directory
    #
    if parser.has_option('hermes', 'remotedir'):
        print("local dir creation", parser.get('hermes', 'localdir'))
        zeus.file.Path(parser.get('hermes', 'localdir'))

    #
    # change to remote directory
    #
    if parser.has_option('hermes', 'remotedir'):
        print("remote chdir to", parser.get('hermes', 'remotedir'))
        connection.chdir(parser.get('hermes', 'remotedir'))

    #
    # download files
    #
    if parser.get('hermes', 'command') == 'get':
        sftp_get(connection)
    elif parser.get('hermes', 'command') == 'put':
        sftp_put(connection)
    else:
        print("ERROR: no supported command")

    #
    # closing connection
    #
    print("closing sftp connexion...")
    connection.close()
    print("sftp connexion closed...OK")

def create_status_backup():

    global statuslogdir, backupdir, statuslogdir_path, backupdir_path

    #
    # create statuslog dir if it does not exist
    #
    date = zeus.date.Date()
    if (parser.get('hermes', 'statuslogdir')):
        statuslogdir = parser.get('hermes', 'statuslogdir')
        statuslogdir_path = zeus.file.Path(date.path_date_tree(statuslogdir))

    #
    # create backupdir if it does not exists
    #
    if (parser.get('hermes', 'backupdir')):
        backupdir = parser.get('hermes', 'backupdir')
        backupdir_path = zeus.file.Path(date.path_date_tree(backupdir))


#
# command line parsing
#
args_parser = argparse.ArgumentParser()
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
    # parse the hermes configuration file
    #
    parser = zeus.parser.ConfigParser(args.file)

    #
    # exit if activation = no
    #
    if parser.get('hermes', 'activation') != 'yes':
        exit("transfer not activated, aborted")

    #
    # SFTP connection
    #
    if parser.get('hermes', 'protocol') == "sftp":
        sftp()
    else:
        print("protocol unsupported", parser.get('hermes', 'protocol'))

#
# exceptions tracking
#
except hermes.exception.AuthenticationException as error:
    print("ERROR: Authentication private key", username, private_key)
except zeus.exception.InvalidConfigurationFileException:
    print("ERROR: invalid configuration file: " + args.file)
except zeus.exception.PrivateKeyException:
    print("ERROR: ZPK variable for zeus key not set")
