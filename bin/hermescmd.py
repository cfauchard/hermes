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

#
# global vars declaration
#
exclude_regex = None
include_regex = None

#
# download function
#
# parameters:
# - file_name: file name to download
#
def sftp_get_file(connection, file):
    statuslogdir = None

    #
    # creating statuslog dir if it does not exist
    #
    date = zeus.date.Date()
    if (parser.get('hermes', 'statuslogdir')):
        statuslogdir = parser.get('hermes', 'statuslogdir')
        statuslogdir_path = zeus.file.Path(date.path_date_tree(statuslogdir))

    try:
        print("download", file, ": size", connection.get_size(file))
        connection.get(file, os.path.join(parser.get('hermes','localdir'), file))
    except:
        status = -1
    else:
        status = 0

    if statuslogdir:
        print("writing in statuslogdir", os.path.join(statuslogdir_path.path, file), status)
        f = open(os.path.join(statuslogdir_path.path, file), 'w')
        f.write("%s;%d;" % (os.path.join(parser.get('hermes','localdir'), file), status))
        f.close()

#
# get command for sftp connection
#
def sftp_get(connection):
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
        else:

            #
            # test if directory
            #
            if connection.is_dir(file):
                print("WARNING:", file, "directory excluded")
            else:

                #
                # test include regex
                #
                if include_regex:
                    if include_regex.match(file):
                        sftp_get_file(connection, file)
                    else:
                        print("WARNING:", file, "excluded by includeregex")
                else:
                    sftp_get_file(connection, file)


#
# upload function
#
# parameters:
# - file_name: file name to upload
#
def sftp_put_file(connection, file):
    print("upload", file, ": size", os.path.getsize(file))


#
# put command for sftp connection
#
def sftp_put(connection):
    #
    # List files in local directory
    #
    for file in os.listdir():

        #
        # exclude directories
        #
        if os.path.isdir(file):
            print("WARNING: ", file, "directory excluded")
        else:
            sftp_put_file(connection, file)


#
# SFTP protocol
#
def sftp():
    print("sftp protocol")

    print("sftp connexion to",
          parser.get('hermes', 'user') + "@" + parser.get('hermes', 'host'))

    if (parser.has_option('hermes', 'private_key')):
        print("private key authentication",
          parser.get('hermes', 'private_key'),
          "..."
          )

        #
        # create an hermes.SFTPConnection object with private key
        #
        connection = hermes.sftp.SFTPConnection(
            parser.get('hermes', 'host'),
            parser.get('hermes', 'user'),
            private_key = parser.get('hermes', 'private_key'))
        print("sftp connexion opened...OK")

    elif (parser.has_option('hermes', 'cryptedpassword')):
        print("password authentication")
        crypted_password = parser.get('hermes', 'cryptedpassword')
        print("crypted password:", crypted_password)
        cipher = zeus.crypto.Vigenere("../sample/hermes.zpk")
        cipher.decrypt(crypted_password)
        password = cipher.get_decrypted_datas().decode("utf8")

        #
        # create an hermes.SFTPConnection object with password
        #
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
    # change remote directory
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


#
# command line parsing
#
args_parser = argparse.ArgumentParser()
args_parser.add_argument("file", help="hermes config file")
args = args_parser.parse_args()

try:

    #
    # display version and config informations
    #
    print("version zeus: " + zeus.__version__)
    print("version hermes: " + hermes.__version__)

    print("hermes config file: " + args.file)

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
    print("Authentication private key", username, private_key, "...ERROR")
except zeus.exception.InvalidConfigurationFileException:
    print("invalid configuration file: " + args.file)
