#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# hermes: sftp.py
#
# Define SFTP connection class based on paramiko package
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import sys
sys.path.insert(0, "../")
import hermes
    
import paramiko, sys
from hermes.exception import AuthenticationException

class SFTPConnection():
    """
    SFTP Class based on Paramiko
    """

    def __init__(self, host, username, port=22, password=None, private_key=None):
        self.host = host
        self.port = port        
        self.username = username
        self.password = password
        self.private_key_file = private_key
        self.sftp = None

        try:
            self.transport = paramiko.Transport((host, port))

            if ( self.private_key_file != None ):
                self.private_key = paramiko.RSAKey.from_private_key_file(self.private_key_file)
                self.transport.connect(username=self.username, pkey=self.private_key)
            elif ( self.password != None ):
                self.transport.connect(username=self.username, password=self.password)
            else:
                raise AuthenticationException(self.username, self.private_key_file) 
                
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        except paramiko.ssh_exception.AuthenticationException as error:
            raise AuthenticationException(self.username, self.private_key_file) from error

    def list(self):
        if self.sftp == None:
            return(None)
        
        return(self.sftp.listdir())

    def get(self, remotepath, localpath=None):
        if localpath == None:
            localpath = remotepath

        try:
            self.sftp.get(remotepath, localpath)           
        except FileNotFoundError:
            raise(FileNotFoundException(remotepath))

    def close(self):   
        if self.transport.is_active():
            self.sftp.close()
 

    def __exit__(self, type, value, tb):
        self.close()

if __name__ == '__main__':

    # host='192.168.1.24'
    # username='root'
    # password='tgmmdm'

    host='xjsd.itnovem.fr'
    username='chris'
    password='tgmmdm!'
    private_key='C:/USBKEY/LiberKey/MyApps/KittyPortable/itnovem_openssh.ppk'

    print("Running tests for sftp.py...")
    print("testing class SFTPConnection...")

    try:
        print("version hermes: " + hermes.__version__)
        print("testing sftp login/password connection...")
        connection = hermes.SFTPConnection(host, username, password=password)
        print("sftp login/password connection...OK")

        print("testing sftp directory listing...")
        directory_list = connection.list()
        print(directory_list)
        print("sftp directory listing...OK")

        print("closing sftp connection...")
        connection.close()
        print("closing sftp connection...OK")                

    except AuthenticationException as error:
        print("Authentication login/password", username,"...ERROR")

    try:
    
        print("testing sftp private key connection...")
        connection = hermes.SFTPConnection(host, username, private_key=private_key)
        print("sftp private key connection... OK")

        print("testing sftp directory listing...")
        directory_list = connection.list()
        print(directory_list)
        print("sftp directory listing...OK")
        
        print("closing sftp connection...")
        connection.close()
        print("closing sftp connection...OK")  
    
    except AuthenticationException as error:
        print("Authentication private key", username, private_key,"...ERROR")
        
