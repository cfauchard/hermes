#!/usr/bin/env python3
# coding: utf-8
#-----------------------------------------------------------------
# hermes: hermesd.py
#
# hermes daemon
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import hermes
import zeus
import argparse
import configparser
import paramiko
import time
import signal

def signint_handler():
    print("signal 15 handled")
    thread_monitor.stop()
    thread_monitor.join()
    thread_monitor.close()

#
# command line parsing
#
args_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
args_parser.add_argument("--version", action='version', version='%(prog)s ' + hermes.__version__)
args_parser.add_argument("config_file", help="""
daemon configuration file

Mandatory keys:

[hermesd]

directory = path of hermes configuration files
logfile = path of the rotated log file
pidfile = path of pid file

""")
args = args_parser.parse_args()

try:


    #
    # instanciate thread monitor
    #
    thread_monitor = hermes.thread.ThreadMonitor(args.config_file)
    thread_monitor.load()

    #
    # install SIGINT handler
    #
    signal.signal(signal.SIGINT, signint_handler)

    thread_monitor.run()
    time.sleep(2)

    #signint_handler()

    thread_monitor.stop()
    thread_monitor.join()
    thread_monitor.close()

#
# exceptions handling
#
except hermes.exception.AuthenticationException as error:
    print("ERROR: authentication exception", error.username, error.private_key)
    connection.last_connection(-1, "authentication exception")
except zeus.exception.InvalidConfigurationFileException as error:
    print("ERROR: invalid configuration file", error.filename)
except zeus.exception.PrivateKeyException:
    print("ERROR: ZPK variable for zeus key not set")
except hermes.exception.ActivationException:
    print("WARNING: not activated")
except hermes.exception.ProtocolUnsupportedException as error:
    print("ERROR: protocol unsupported", error.protocol)
except configparser.NoOptionError as error:
    print("ERROR missing key", error.option, "in section", error.section)
except hermes.exception.CommandUnsupportedException as error:
    print("ERROR unsupported command", error.command)
except hermes.exception.ChdirException as error:
    print("ERROR change directory", error.dir)
except zeus.exception.FileNotFoundException as error:
    print("ERROR file not found", error.filename)
except zeus.exception.DirectoryNotFoundException as error:
    print("ERROR directory not found", error.directory)
except paramiko.ssh_exception.SSHException as error:
    print("ERROR sftp connexion", error.username)