#-----------------------------------------------------------------
# hermes: sftp.py
#
# Define SFTP connection class based on paramiko package
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import hermes, paramiko
from hermes.connection import Connection
from hermes.exception import AuthenticationException

class SFTPConnection(Connection):
    """
    SFTP Class based on Paramiko
    """

    def __init__(self, host, username, port=22, password=None, private_key=None):
        Connection.__init__(self, host, port)
        self.username = username
        self.password = password

        try:
            self.transport.connect(username=username, password=password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        except paramiko.ssh_exception.AuthenticationException:
            raise AuthenticationException(username, password, private_key)

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
    
    host='192.168.1.24'
    username='root'
    password='tgmmdm'

##    host='xjsd.itnovem.fr'
##    username='chris'
##    password='tgmmdm!'

    try:
        print("version hermes: " + hermes.__version__)
        connection = hermes.SFTPConnection(host, username, password=password)

    except hermes.AuthenticationException as error:
        print("Authentication error:", error.username, error.password)
    except:
        print("Unexpected error:", sys.exc_info()[0])

    try:
        directory_list = connection.list()
        print(directory_list)
        connection.close()

    except NameError:
        print("SFTP connection not established")
    except:
        print("Unexpected error:", sys.exc_info()[0])

