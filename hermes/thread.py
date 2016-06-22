#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# hermes: thread.py
#
# Multithread capabilities
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import threading
import time

class ThreadedConnection(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("Starting", self.threadID, self.name)
        time.sleep(10)
        print("Exiting", self.threadID, self.name)