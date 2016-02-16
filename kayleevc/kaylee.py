# This is part of Kaylee
# -- this code is licensed GPLv3
# Copyright 2015-2016 Clayton G. Hobbs
# Portions Copyright 2013 Jezra

import sys
import signal
import os.path
import subprocess
from gi.repository import GObject, GLib

from kayleevc.recognizer import Recognizer
from kayleevc.util import *
from kayleevc.numbers import NumberParser


class Kaylee:

    def __init__(self):
        self.ui = None
        self.options = {}
        ui_continuous_listen = False
        self.continuous_listen = False

        # Load configuration
        self.config = Config()
        self.options = vars(self.config.options)
        self.commands = self.options['commands']

        # Create number parser for later use
        self.number_parser = NumberParser()

        # Create a hasher
        self.hasher = Hasher(self.config)

        # Create the strings file
        self.update_voice_commands_if_changed()

        if self.options['interface']:
            if self.options['interface'] == "g":
                from kayleevc.gui import GTKInterface as UI
            elif self.options['interface'] == "gt":
                from kayleevc.gui import GTKTrayInterface as UI
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
        self.language_updater = LanguageUpdater(self.config)
        self.language_updater.update_language_if_changed()

        # Create the recognizer
        self.recognizer = Recognizer(self.config)
        self.recognizer.connect('finished', self.recognizer_finished)

    def update_voice_commands_if_changed(self):
        """Use hashes to test if the voice commands have changed"""
        stored_hash = self.hasher['voice_commands']

        # Calculate the hash the voice commands have right now
        hasher = self.hasher.get_hash_object()
        for voice_cmd in self.commands.keys():
            hasher.update(voice_cmd.encode('utf-8'))
            # Add a separator to avoid odd behavior
            hasher.update('\n'.encode('utf-8'))
        new_hash = hasher.hexdigest()

        if new_hash != stored_hash:
            self.create_strings_file()
            self.hasher['voice_commands'] = new_hash
            self.hasher.store()

    def create_strings_file(self):
        # Open the strings file
        with open(self.config.strings_file, 'w') as strings:
            # Add command words to the corpus
            for voice_cmd in sorted(self.commands.keys()):
                strings.write(voice_cmd.strip().replace('%d', '') + "\n")
            # Add number words to the corpus
            for word in self.number_parser.number_words:
                strings.write(word + "\n")

    def log_history(self, text):
        if self.options['history']:
            self.history.append(text)
            if len(self.history) > self.options['history']:
                # Pop off the first item
                self.history.pop(0)

            # Open and truncate the history file
            with open(self.config.history_file, 'w') as hfile:
                for line in self.history:
                    hfile.write(line + '\n')

    def run_command(self, cmd):
        """Print the command, then run it"""
        print(cmd)
        subprocess.call(cmd, shell=True)

    def recognizer_finished(self, recognizer, text):
        t = text.lower()
        numt, nums = self.number_parser.parse_all_numbers(t)
        # Is there a matching command?
        if t in self.commands:
            # Run the valid_sentence_command if it's set
            if self.options['valid_sentence_command']:
                subprocess.call(self.options['valid_sentence_command'],
                                shell=True)
            cmd = self.commands[t]
            # Should we be passing words?
            if self.options['pass_words']:
                cmd += " " + t
            self.run_command(cmd)
            self.log_history(text)
        elif numt in self.commands:
            # Run the valid_sentence_command if it's set
            if self.options['valid_sentence_command']:
                subprocess.call(self.options['valid_sentence_command'],
                                shell=True)
            cmd = self.commands[numt]
            cmd = cmd.format(*nums)
            # Should we be passing words?
            if self.options['pass_words']:
                cmd += " " + t
            self.run_command(cmd)
            self.log_history(text)
        else:
            # Run the invalid_sentence_command if it's set
            if self.options['invalid_sentence_command']:
                subprocess.call(self.options['invalid_sentence_command'],
                                shell=True)
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
            self.recognizer.listen()

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
        local_data = os.path.join(os.path.dirname(__file__), '..', 'data')
        paths = ["/usr/share/kaylee/", "/usr/local/share/kaylee", local_data]
        for path in paths:
            resource = os.path.join(path, string)
            if os.path.exists(resource):
                return resource
        # If we get this far, no resource was found
        return False


def run():
    # Make our kaylee object
    kaylee = Kaylee()
    # Init gobject threads
    GObject.threads_init()
    # We want a main loop
    main_loop = GObject.MainLoop()
    # Handle sigint
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Run the kaylee
    kaylee.run()
    # Start the main loop
    try:
        main_loop.run()
    except:
        print("time to quit")
        main_loop.quit()
        sys.exit()
