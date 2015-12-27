#!/usr/bin/env python3

# This is part of Kaylee
# -- this code is licensed GPLv3
# Copyright 2013 Jezra
# Copyright 2015 Clayton G. Hobbs

from __future__ import print_function
import sys
import signal
import hashlib
import os.path
import subprocess
from argparse import ArgumentParser
from gi.repository import GObject
import json
try:
    import yaml
except:
    print("YAML is not supported; unable to use config file")

from recognizer import Recognizer

# Where are the files?
conf_dir = os.path.expanduser("~/.config/blather")
lang_dir = os.path.join(conf_dir, "language")
command_file = os.path.join(conf_dir, "commands.conf")
strings_file = os.path.join(conf_dir, "sentences.corpus")
history_file = os.path.join(conf_dir, "blather.history")
opt_file = os.path.join(conf_dir, "options.json")
hash_file = os.path.join(conf_dir, "hash.yaml")
lang_file = os.path.join(lang_dir, 'lm')
dic_file = os.path.join(lang_dir, 'dic')
# Make the lang_dir if it doesn't exist
if not os.path.exists(lang_dir):
    os.makedirs(lang_dir)

class Blather:

    def __init__(self, opts):
        self.ui = None
        self.options = {}
        ui_continuous_listen = False
        self.continuous_listen = False

        self.commands = {}

        # Read the commands
        self.read_commands()

        # Load the options file
        self.load_options()

        print(opts)
        # Merge the options with the ones provided by command-line arguments
        for k, v in vars(opts).items():
            if v is not None:
                self.options[k] = v

        if self.options['interface'] != None:
            if self.options['interface'] == "g":
                from gtkui import UI
            elif self.options['interface'] == "gt":
                from gtktrayui import UI
            else:
                print("no GUI defined")
                sys.exit()

            self.ui = UI(args, self.options['continuous'])
            self.ui.connect("command", self.process_command)
            # Can we load the icon resource?
            icon = self.load_resource("icon.png")
            if icon:
                self.ui.set_icon_active_asset(icon)
            # Can we load the icon_inactive resource?
            icon_inactive = self.load_resource("icon_inactive.png")
            if icon_inactive:
                self.ui.set_icon_inactive_asset(icon_inactive)

        if self.options['history']:
            self.history = []

        # Update the language if necessary
        self.update_language()

        # Create the recognizer
        try:
            self.recognizer = Recognizer(lang_file, dic_file, self.options['microphone'])
        except Exception as e:
            # No recognizer? bummer
            print('error making recognizer')
            sys.exit()

        self.recognizer.connect('finished', self.recognizer_finished)

        print("Using Options: ", self.options)

    def read_commands(self):
        # Read the commands file
        file_lines = open(command_file)
        strings = open(strings_file, "w")
        for line in file_lines:
            print(line)
            # Trim the white spaces
            line = line.strip()
            # If the line has length and the first char isn't a hash
            if len(line) and line[0]!="#":
                # This is a parsible line
                (key, value) = line.split(":", 1)
                print(key, value)
                self.commands[key.strip().lower()] = value.strip()
                strings.write( key.strip()+"\n")
        # Close the strings file
        strings.close()

    def load_options(self):
        """Load options from the options.json file"""
        # Is there an opt file?
        with open(opt_file, 'r') as f:
            self.options = json.load(f)
            print(self.options)

    def log_history(self, text):
        if self.options['history']:
            self.history.append(text)
            if len(self.history) > self.options['history']:
                # Pop off the first item
                self.history.pop(0)

            # Open and truncate the blather history file
            hfile = open(history_file, "w")
            for line in self.history:
                hfile.write( line+"\n")
            # Close the file
            hfile.close()

    def update_language(self):
        """Update the language if its hash has changed"""
        try:
            # Load the stored hash from the hash file
            try:
                with open(hash_file, 'r') as f:
                    text = f.read()
                    hashes = yaml.load(text)
                stored_hash = hashes['language']
            except (IOError, KeyError, TypeError):
                # No stored hash
                stored_hash = ''

            # Calculate the hash the language file has right now
            hasher = hashlib.sha256()
            with open(strings_file, 'rb') as sfile:
                buf = sfile.read()
                hasher.update(buf)
            new_hash = hasher.hexdigest()

            # If the hashes differ
            if stored_hash != new_hash:
                # Update the language
                # FIXME: Do this with Python, not Bash
                self.run_command('./language_updater.sh')
                # Store the new hash
                new_hashes = {'language': new_hash}
                with open(hash_file, 'w') as f:
                    f.write(yaml.dump(new_hashes))
        except Exception as e:
            # Do nothing if the hash file cannot be loaded
            # FIXME: This is kind of bad; maybe YAML should be mandatory.
            print('error updating language')
            print(e)
            pass

    def run_command(self, cmd):
        """Print the command, then run it"""
        print(cmd)
        subprocess.call(cmd, shell=True)

    def recognizer_finished(self, recognizer, text):
        t = text.lower()
        # Is there a matching command?
        if t in self.commands:
            # Run the valid_sentence_command if there is a valid sentence command
            if self.options['valid_sentence_command']:
                subprocess.call(self.options['valid_sentence_command'], shell=True)
            cmd = self.commands[t]
            # Should we be passing words?
            if self.options['pass_words']:
                cmd += " " + t
                self.run_command(cmd)
            else:
                self.run_command(cmd)
            self.log_history(text)
        else:
            # Run the invalid_sentence_command if there is an invalid sentence command
            if self.options['invalid_sentence_command']:
                subprocess.call(self.options['invalid_sentence_command'], shell=True)
            print("no matching command {0}".format(t))
        # If there is a UI and we are not continuous listen
        if self.ui:
            if not self.continuous_listen:
                # Stop listening
                self.recognizer.pause()
            # Let the UI know that there is a finish
            self.ui.finished(t)

    def run(self):
        if self.ui:
            self.ui.run()
        else:
            blather.recognizer.listen()

    def quit(self):
        sys.exit()

    def process_command(self, UI, command):
        print(command)
        if command == "listen":
            self.recognizer.listen()
        elif command == "stop":
            self.recognizer.pause()
        elif command == "continuous_listen":
            self.continuous_listen = True
            self.recognizer.listen()
        elif command == "continuous_stop":
            self.continuous_listen = False
            self.recognizer.pause()
        elif command == "quit":
            self.quit()

    def load_resource(self, string):
        local_data = os.path.join(os.path.dirname(__file__), 'data')
        paths = ["/usr/share/blather/", "/usr/local/share/blather", local_data]
        for path in paths:
            resource = os.path.join(path, string)
            if os.path.exists( resource ):
                return resource
        # If we get this far, no resource was found
        return False


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--interface",  type=str, dest="interface",
            action='store',
            help="Interface to use (if any). 'g' for GTK or 'gt' for GTK system tray icon")

    parser.add_argument("-c", "--continuous",
            action="store_true", dest="continuous", default=False,
            help="starts interface with 'continuous' listen enabled")

    parser.add_argument("-p", "--pass-words",
            action="store_true", dest="pass_words", default=False,
            help="passes the recognized words as arguments to the shell command")

    parser.add_argument("-H", "--history", type=int,
            action="store", dest="history",
            help="number of commands to store in history file")

    parser.add_argument("-m", "--microphone", type=int,
            action="store", dest="microphone", default=None,
            help="Audio input card to use (if other than system default)")

    parser.add_argument("--valid-sentence-command",  type=str, dest="valid_sentence_command",
            action='store',
            help="command to run when a valid sentence is detected")

    parser.add_argument( "--invalid-sentence-command",  type=str, dest="invalid_sentence_command",
            action='store',
            help="command to run when an invalid sentence is detected")

    args = parser.parse_args()
    # Make our blather object
    blather = Blather(args)
    # Init gobject threads
    GObject.threads_init()
    # We want a main loop
    main_loop = GObject.MainLoop()
    # Handle sigint
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Run the blather
    blather.run()
    # Start the main loop
    try:
        main_loop.run()
    except:
        print("time to quit")
        main_loop.quit()
        sys.exit()

