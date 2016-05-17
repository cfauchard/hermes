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
sys.path.insert(0, "../../lib")

import zeus
import hermes
import argparse

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
        print("closing sftp connexion...")
        connection.close()
        print("sftp connexion closed...OK")
    else: 
        print("default protocol: ftp")
    
except hermes.AuthenticationException as error:
        print("Authentication private key", username, private_key,"...ERROR")
except zeus.exception.InvalidConfigurationFileException:
    print("fichier de configuration " + args.file + " invalide")

