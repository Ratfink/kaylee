# This is part of Kaylee
# -- this code is licensed GPLv3
# Copyright 2013 Jezra
# Copyright 2015 Clayton G. Hobbs

import json
import os
from argparse import ArgumentParser, Namespace

from gi.repository import GLib

class Config:
    """Keep track of the configuration of Kaylee"""
    # Name of the program, for later use
    program_name = "kaylee"

    # Directories
    conf_dir = os.path.join(GLib.get_user_config_dir(), program_name)
    cache_dir = os.path.join(GLib.get_user_cache_dir(), program_name)
    data_dir = os.path.join(GLib.get_user_data_dir(), program_name)

    # Configuration files
    command_file = os.path.join(conf_dir, "commands.conf")
    opt_file = os.path.join(conf_dir, "options.json")

    # Cache files
    history_file = os.path.join(cache_dir, program_name + "history")
    hash_file = os.path.join(cache_dir, "hash.json")

    # Data files
    strings_file = os.path.join(data_dir, "sentences.corpus")
    lang_file = os.path.join(data_dir, 'lm')
    dic_file = os.path.join(data_dir, 'dic')

    def __init__(self):
        # Ensure necessary directories exist
        self._make_dir(self.conf_dir)
        self._make_dir(self.cache_dir)
        self._make_dir(self.data_dir)

        # Set up the argument parser
        self.parser = ArgumentParser()
        self.parser.add_argument("-i", "--interface", type=str,
                dest="interface", action='store',
                help="Interface to use (if any). 'g' for GTK or 'gt' for GTK" +
                " system tray icon")

        self.parser.add_argument("-c", "--continuous",
                action="store_true", dest="continuous", default=False,
                help="Start interface with 'continuous' listen enabled")

        self.parser.add_argument("-p", "--pass-words",
                action="store_true", dest="pass_words", default=False,
                help="Pass the recognized words as arguments to the shell" +
                " command")

        self.parser.add_argument("-H", "--history", type=int,
                action="store", dest="history",
                help="Number of commands to store in history file")

        self.parser.add_argument("-m", "--microphone", type=int,
                action="store", dest="microphone", default=None,
                help="Audio input card to use (if other than system default)")

        self.parser.add_argument("--valid-sentence-command", type=str,
                dest="valid_sentence_command", action='store',
                help="Command to run when a valid sentence is detected")

        self.parser.add_argument("--invalid-sentence-command", type=str,
                dest="invalid_sentence_command", action='store',
                help="Command to run when an invalid sentence is detected")

        # Read the configuration file
        self._read_options_file()

        # Parse command-line arguments, overriding config file as appropriate
        self.parser.parse_args(namespace=self.options)

    def _make_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def _read_options_file(self):
        try:
            with open(self.opt_file, 'r') as f:
                self.options = json.load(f)
                self.options = Namespace(**self.options)
        except FileNotFoundError:
            # Make an empty options namespace
            self.options = Namespace()
