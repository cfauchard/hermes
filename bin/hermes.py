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
sys.path.insert(0, "../")
sys.path.insert(0, "../../zeus")

import zeus
import hermes
import argparse
import re
import stat

parser = argparse.ArgumentParser()
parser.add_argument("file", help="hermes config file")
args = parser.parse_args()

try:
    print("version zeus: " + zeus.__version__)
    print("version hermes: " + hermes.__version__)
    parser = zeus.ConfigParser(args.file)
    
    print("hermes config file: " + parser.file_name)
    if parser.get('hermes', 'activation') != 'yes':
        exit("transfer not activated, aborted")
    
    #
    # SFTP connection
    #
    if parser.has_section('sftp'):
        print("sftp protocol")
        print("sftp connexion to",
            parser.get('hermes', 'user') + "@" + parser.get('hermes', 'host'),
            "with private key",
            parser.get('sftp', 'private_key'),
            "..."
            )
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

        if parser.has_option('hermes', 'includeregex'):
            exclude_regex = re.compile(parser.get('hermes', 'includeregex'))
            
        #
        # List files in directory
        #
        list_files = connection.list()
        for file in list_files:
            if exclude_regex.match(file):
                print("WARNING: ", file, "excluded")
            else:
                if connection.is_dir(file):
                    print("WARNING:", file, "directory")
                else:
                    print(file, ": size", connection.get_size(file))
        
        print("closing sftp connexion...")
        connection.close()
        print("sftp connexion closed...OK")
    else: 
        print("default protocol: ftp")
    
except hermes.AuthenticationException as error:
        print("Authentication private key", username, private_key,"...ERROR")
except zeus.exception.InvalidConfigurationFileException:
    print("fichier de configuration " + args.file + " invalide")

