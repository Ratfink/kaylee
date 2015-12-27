# This is part of Kaylee
# -- this code is licensed GPLv3
# Copyright 2013 Jezra
# Copyright 2015 Clayton G. Hobbs

import json
import os
from argparse import ArgumentParser, Namespace

from gi.repository import GLib

class Config:
    conf_dir = os.path.expanduser(os.path.join(GLib.get_user_config_dir(),
                                               "blather"))
    opt_file = os.path.join(conf_dir, "options.json")

    def __init__(self):
        # Set up the argument parser
        self.parser = ArgumentParser()
        self.parser.add_argument("-i", "--interface", type=str,
                dest="interface", action='store',
                help="Interface to use (if any). 'g' for GTK or 'gt' for GTK" +
                " system tray icon")

        self.parser.add_argument("-c", "--continuous",
                action="store_true", dest="continuous", default=False,
                help="starts interface with 'continuous' listen enabled")

        self.parser.add_argument("-p", "--pass-words",
                action="store_true", dest="pass_words", default=False,
                help="passes the recognized words as arguments to the shell" +
                " command")

        self.parser.add_argument("-H", "--history", type=int,
                action="store", dest="history",
                help="number of commands to store in history file")

        self.parser.add_argument("-m", "--microphone", type=int,
                action="store", dest="microphone", default=None,
                help="Audio input card to use (if other than system default)")

        self.parser.add_argument("--valid-sentence-command", type=str,
                dest="valid_sentence_command", action='store',
                help="command to run when a valid sentence is detected")

        self.parser.add_argument("--invalid-sentence-command", type=str,
                dest="invalid_sentence_command", action='store',
                help="command to run when an invalid sentence is detected")

        # Read the configuration file
        with open(self.opt_file, 'r') as f:
            self.options = json.load(f)
            self.options = Namespace(**self.options)

        # Parse command-line arguments, overriding config file as appropriate
        self.args = self.parser.parse_args(namespace=self.options)
