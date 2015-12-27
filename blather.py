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
from gi.repository import GObject, GLib
import json

from recognizer import Recognizer
from config import Config


class Blather:

    def __init__(self):
        self.ui = None
        self.options = {}
        ui_continuous_listen = False
        self.continuous_listen = False

        self.commands = {}

        # Load configuration
        self.config = Config()
        self.options = vars(self.config.options)

        # Read the commands
        self.read_commands()

        if self.options['interface'] != None:
            if self.options['interface'] == "g":
                from gtkui import UI
            elif self.options['interface'] == "gt":
                from gtktrayui import UI
            else:
                print("no GUI defined")
                sys.exit()

            self.ui = UI(self.options, self.options['continuous'])
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
        self.recognizer = Recognizer(self.config)
        self.recognizer.connect('finished', self.recognizer_finished)

    def read_commands(self):
        # Read the commands file
        file_lines = open(self.config.command_file)
        strings = open(self.config.strings_file, "w")
        for line in file_lines:
            # Trim the white spaces
            line = line.strip()
            # If the line has length and the first char isn't a hash
            if len(line) and line[0] != "#":
                # This is a parsible line
                (key, value) = line.split(":", 1)
                self.commands[key.strip().lower()] = value.strip()
                strings.write(key.strip() + "\n")
        # Close the strings file
        strings.close()

    def log_history(self, text):
        if self.options['history']:
            self.history.append(text)
            if len(self.history) > self.options['history']:
                # Pop off the first item
                self.history.pop(0)

            # Open and truncate the blather history file
            hfile = open(self.config.history_file, "w")
            for line in self.history:
                hfile.write(line + "\n")
            # Close the file
            hfile.close()

    def update_language(self):
        """Update the language if its hash has changed"""
        # Load the stored hash from the hash file
        try:
            with open(self.config.hash_file, 'r') as f:
                hashes = json.load(f)
            stored_hash = hashes['language']
        except (IOError, KeyError, TypeError):
            # No stored hash
            stored_hash = ''

        # Calculate the hash the language file has right now
        hasher = hashlib.sha256()
        with open(self.config.strings_file, 'rb') as sfile:
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
            with open(self.config.hash_file, 'w') as f:
                json.dump(new_hashes, f)

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
            if os.path.exists(resource):
                return resource
        # If we get this far, no resource was found
        return False


if __name__ == "__main__":
    # Make our blather object
    blather = Blather()
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

