#!/usr/bin/env python3
# coding: utf8
# -----------------------------------------------------------------
# hermes: thread.py
#
# Multithread capabilities
#
# Copyright (C) 2016, Christophe Fauchard
# -----------------------------------------------------------------
"""
Submodule: hermes.thread

Hermes submodule, multithread task classes

Copyright (C) 2016-2017, Christophe Fauchard
"""

import threading
import time
import zeus
import hermes
import glob
import os


class ThreadedConnection(threading.Thread):
    def __init__(self, chain_name, hermes_config_files):
        threading.Thread.__init__(self)
        self._is_running = True
        self.chain_name = chain_name
        self.hermes_config_files = hermes_config_files

    def run(self):
        print("Starting", self.getName())
        while self._is_running is True:
            print("computing %s for chain %s..." % (
                self.getName(), self.chain_name))

            for hermes_config_file in self.hermes_config_files:
                print("launching hermes connection with config file %s"
                      % hermes_config_file)

                #
                # create an hermes connection object
                #
                # self.connection = hermes.connection.Connection(
                #    hermes_config_file)
                # self.connection.log.set_level(logging.INFO)
                # self.connection.connect()
                # self.connection.start()
                # self.connection.close()

            print("sleeping...")
            time.sleep(1)
        print("Exiting", self.getName())

    def stop(self):
        self._is_running = False


class ThreadMonitor():
    def __init__(self, hermesd_config_file):

        #
        # create an ini file parser and read config file
        #
        self.parser = zeus.parser.ConfigParser(hermesd_config_file)

        #
        # logfile
        #
        if self.parser.has_option('hermesd', 'logfile'):

            #
            # create 512Ko switch log
            #
            self.log = zeus.log.Log(
                self.parser.get('hermesd', 'logfile'),
                size=1024 * 512
            )
        else:

            #
            # create an stdout only logger
            #
            self.log = zeus.log.Log()

        self.log.logger.info(
            "initializing Hermes thread monitor with %s", hermesd_config_file)
        self.log.logger.info("hermes %s", hermes.__version__)
        self.log.logger.info("zeus %s", zeus.__version__)

        #
        # create pid file
        #
        self.pidfile = self.parser.get("hermesd", "pidfile")
        fd = open(self.pidfile, "w")
        fd.write("%d" % os.getpid())
        fd.close()

        self.directory = self.parser.get('hermesd', 'directory')

        if not os.path.isdir(self.directory):
            self.log.logger.error(
                "hermes config file directory not found: %s", self.directory)
            raise zeus.exception.DirectoryNotFoundException(self.directory)

    def load(self):
        self.threads = []

        #
        # list hermes files in directory and initialise threads
        #
        # for hermes_file in glob.glob(
        #         self.parser.get('hermesd', 'directory') + "/*.hermes"):

        for chain in self.parser.items("monitor"):
            self.log.logger.info(
                "adding chain for hermes config file %s", chain)

            hermes_files = []
            for hermes_file in self.parser.get("monitor", chain[0]).split(','):
                self.log.logger.info(
                    "adding hermes config file %s for chain %s",
                    hermes_file.lstrip(), chain[0])
                hermes_files.append(hermes_file.lstrip().rstrip())

            self.log.logger.info(
                "adding thread for hermes config files %s", hermes_files)
            thread = hermes.thread.ThreadedConnection(chain[0], hermes_files)
            self.threads.append(thread)
            self.log.logger.info("number of threads: %d", len(self.threads))

    def run(self):

        for thread in self.threads:
            self.log.logger.info(
                "starting thread for chain %s", thread.chain_name)
            thread.start()

    def stop(self):

        for thread in self.threads:
            self.log.logger.info(
                "stopping thread for chain %s", thread.chain_name)
            thread.stop()

    def join(self):

        for thread in self.threads:
            self.log.logger.info(
                "waiting for thread termination %s", thread.getName())
            thread.stop()

    def close(self):
        self.log.logger.info("remove pidfile %s", self.pidfile)
        self.log.logger.info("closing hermes thread monitor")
        os.remove(self.pidfile)
