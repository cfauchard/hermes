#-----------------------------------------------------------------
# hermes: connection.py
#
# Define generic connection class
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import hermes
import paramiko

class Connection:
    """
    Generic Hermes Connection
    """
    
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.transport = paramiko.Transport((host, port))

    def close(self):
        if self.transport.is_active():
            self.transport.close()

    def __exit__(self, type, value, tb):
        self.close()
        
