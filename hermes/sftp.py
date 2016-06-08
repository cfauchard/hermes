#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# hermes: sftp.py
#
# Define SFTP connection class based on paramiko package
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import stat
import hermes
    
import paramiko, sys
from hermes.exception import AuthenticationException

class SFTPConnection():

    """
    SFTP Class based on Paramiko
    
    Attributes:
    - host
    - port
    - username
    - password
    - private_key_file
    - sftp: paramiko.SFTPClient object
    - transport: paramiko.Transport object
    
    Methods:
    - chdir(dir)
    - list()
    - bool is_dir(path)
    - int get_size(path)
    - get(remotepath, localpath=None)
    - put(localpath, remotepath=None)
    - remove(path)
    - close()
    """

    def __init__(self, host, username, port=22, password=None, private_key=None):
        self.host = host
        self.port = port        
        self.username = username
        self.password = password
        self.private_key_file = private_key
        self.sftp = None

        #
        # Open SFTP connection
        #
        try:
            
            #
            # open transport connection
            #
            self.transport = paramiko.Transport((host, port))

            #
            # authentication by private key
            #
            if ( self.private_key_file != None ):
                self.private_key = paramiko.RSAKey.from_private_key_file(self.private_key_file)
                self.transport.connect(username=self.username, pkey=self.private_key)
            
            #
            # authentication by login/password
            #
            elif ( self.password != None ):
                self.transport.connect(username=self.username, password=self.password)
            else:
                raise AuthenticationException(self.username, self.private_key_file) 
                
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            
        except paramiko.ssh_exception.AuthenticationException as error:
            raise AuthenticationException(self.username, self.private_key_file) from error

    #
    # chdir
    #
    def chdir(self, dir):
        try:
            if not self.sftp == None:
                self.sftp.chdir(dir)
        except:
            raise hermes.exception.ChdirException(dir)
    #
    # list files
    #
    def list(self):
        if self.sftp == None:
            return(None)
        
        return(self.sftp.listdir())
    
    #
    # test if the remote file is a directory
    #
    def is_dir(self, path):
        st = self.sftp.lstat(path)
        if stat.S_ISDIR(st.st_mode):
            return(True)
        else:
            return(False)
    
    #
    # get the remote file size
    #
    def get_size(self, path):
        if self.is_dir(path):
            return(0)
    
        st = self.sftp.lstat(path)
        return(st.st_size)

    #
    # download a file
    #
    def get(self, remotepath, localpath=None):
        if localpath == None:
            localpath = remotepath

        self.sftp.get(remotepath, localpath)           
 
    #
    # upload a file
    #
    def put(self, localpath, remotepath=None):
        if remotepath == None:
            remotepath = localpath

        self.sftp.put(localpath, remotepath)           
                        
    #
    # remove remote path
    #
    def remove(self, path):
        if not self.is_dir(path):
            self.sftp.remove(path)

    #
    # remove remote path
    #
    def rename(self, src, dest):
        self.sftp.rename(src, dest)

    #
    # close the connection
    #
    def close(self):   
        if self.transport.is_active():
            self.sftp.close()
 

    def __exit__(self, type, value, tb):
        self.close()


