#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# hermescmd: hermes.py
#
# hermes command line tool
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import sys
import pypath
import os
import hermes
import zeus
import argparse
import re
import stat

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
    print("download", file, ": size", connection.get_size(file))
    connection.get(file)

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
            parser.get('hermes', 'user') + "@" + parser.get('hermes', 'host'),
            "with private key",
            parser.get('sftp', 'private_key'),
            "..."
            )
            
        #
        # create an hermes.SFTPConnection object
        #
        connection = hermes.SFTPConnection(
            parser.get('hermes', 'host'),
            parser.get('hermes', 'user'), 
            private_key=parser.get('sftp', 'private_key'))
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
            print("local chdir to", parser.get('hermes', 'localdir'))
            os.chdir(parser.get('hermes', 'localdir'))        
        
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
parser = argparse.ArgumentParser()
parser.add_argument("file", help="hermes config file")
args = parser.parse_args()
    
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
    parser = zeus.ConfigParser(args.file)
    
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
except hermes.AuthenticationException as error:
    print("Authentication private key", username, private_key,"...ERROR")
except zeus.exception.InvalidConfigurationFileException:
    print("invalid configuration file: " + args.file)