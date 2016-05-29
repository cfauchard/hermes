#-----------------------------------------------------------------
# hermes: ftp.py
#
# Define FTP connection class based on ftplib
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import ftplib
from ftplib import FTP


class FTPConnection(FTP):
    """
    Surcouche d'abstraction SFTP basée sur ftplib
    """

    def __init__(self, host, username, port=21, password=None):
        FTP.__init__(self, host)
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        try:
            self.connect(self.host)
        except ftplib.all_errors:
            raise ConnectionException(username, password)

        try:
            self.login(username, password)
        except ftplib.all_errors:
            raise AuthenticationException(username, password)            

    def list(self):
        return(self.nlst())
    
    def get(self, remotepath, localpath=None):
        if localpath == None:
            localpath = remotepath

        try:
            self.retrbinary('RETR ' + remotepath, open(localpath, 'wb').write)
        except FileNotFoundError:
            print("File not found: " + remotepath)
        except:
            print("Unexpected error:", sys.exc_info()[0])

    def __exit__(self, type, value, tb):
        self.quit()
        self.close()


        

