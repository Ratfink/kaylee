#!/usr/bin/env python2

# -- this code is licensed GPLv3
# Copyright 2013 Jezra

import sys
import signal
import gobject
import os.path
import subprocess
from optparse import OptionParser
try:
	import yaml
except:
	print "YAML is not supported. ~/.config/blather/options.yaml will not function"

#where are the files?
conf_dir = os.path.expanduser("~/.config/blather")
lang_dir = os.path.join(conf_dir, "language")
command_file = os.path.join(conf_dir, "commands.conf")
strings_file = os.path.join(conf_dir, "sentences.corpus")
history_file = os.path.join(conf_dir, "blather.history")
opt_file = os.path.join(conf_dir, "options.yaml")
lang_file = os.path.join(lang_dir,'lm')
dic_file = os.path.join(lang_dir,'dic')
#make the lang_dir if it doesn't exist
if not os.path.exists(lang_dir):
	os.makedirs(lang_dir)

class Blather:
	def __init__(self, opts):

		#import the recognizer so Gst doesn't clobber our -h
		from Recognizer import Recognizer
		self.ui = None
		self.options = {}
		ui_continuous_listen = False
		self.continuous_listen = False

		self.commands = {}

		#read the commands
		self.read_commands()

		#load the options file
		self.load_options()

		#merge the opts
		for k,v in opts.__dict__.items():
			if (not k in self.options) or opts.override:
				self.options[k] = v

		print "Using Options: ", self.options

		if self.options['interface'] != None:
			if self.options['interface'] == "q":
				from QtUI import UI
			elif self.options['interface'] == "g":
				from GtkUI import UI
			elif self.options['interface'] == "gt":
				from GtkTrayUI import UI
			else:
				print "no GUI defined"
				sys.exit()

			self.ui = UI(args, self.options['continuous'])
			self.ui.connect("command", self.process_command)
			#can we load the icon resource?
			icon = self.load_resource("icon.png")
			if icon:
				self.ui.set_icon_active_asset(icon)
			#can we load the icon_inactive resource?
			icon_inactive = self.load_resource("icon_inactive.png")
			if icon_inactive:
				self.ui.set_icon_inactive_asset(icon_inactive)

		if self.options['history']:
			self.history = []

		#create the recognizer
		self.recognizer = Recognizer(lang_file, dic_file, self.options['microphone'] )
		self.recognizer.connect('finished',self.recognizer_finished)

	def read_commands(self):
		#read the.commands file
		file_lines = open(command_file)
		strings = open(strings_file, "w")
		for line in file_lines:
				print line
				#trim the white spaces
				line = line.strip()
				#if the line has length and the first char isn't a hash
				if len(line) and line[0]!="#":
						#this is a parsible line
						(key,value) = line.split(":",1)
						print key, value
						self.commands[key.strip().lower()] = value.strip()
						strings.write( key.strip()+"\n")
		#close the strings file
		strings.close()

	def load_options(self):
		#is there an opt file?
		try:
			opt_fh = open(opt_file)
			text = opt_fh.read()
			self.options = yaml.load(text)
		except:
			pass


	def log_history(self,text):
		if self.options['history']:
			self.history.append(text)
			if len(self.history) > self.options['history']:
				#pop off the first item
				self.history.pop(0)

			#open and truncate the blather history file
			hfile = open(history_file, "w")
			for line in self.history:
				hfile.write( line+"\n")
			#close the  file
			hfile.close()

	def recognizer_finished(self, recognizer, text):
		t = text.lower()
		#is there a matching command?
		if self.commands.has_key( t ):
			#run the valid_sentence_command if there is a valid sentence command
			if self.options['valid_sentence_command']:
				subprocess.call(self.options['valid_sentence_command'], shell=True)
			cmd = self.commands[t]
			print cmd
			subprocess.call(cmd, shell=True)
			self.log_history(text)
		else:
			#run the invalid_sentence_command if there is a valid sentence command
			if self.options['invalid_sentence_command']:
				subprocess.call(self.options['invalid_sentence_command'], shell=True)
			print "no matching command %s" %(t)
		#if there is a UI and we are not continuous listen
		if self.ui:
			if not self.continuous_listen:
				#stop listening
				self.recognizer.pause()
			#let the UI know that there is a finish
			self.ui.finished(t)

	def run(self):
		if self.ui:
			self.ui.run()
		else:
			blather.recognizer.listen()

	def quit(self):
		sys.exit()

	def process_command(self, UI, command):
		print command
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

	def load_resource(self,string):
		local_data = os.path.join(os.path.dirname(__file__), 'data')
		paths = ["/usr/share/blather/","/usr/local/share/blather", local_data]
		for path in paths:
			resource = os.path.join(path, string)
			if os.path.exists( resource ):
				return resource
		#if we get this far, no resource was found
		return False


if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-i", "--interface",  type="string", dest="interface",
		action='store',
		help="Interface to use (if any). 'q' for Qt, 'g' for GTK, 'gt' for GTK system tray icon")

	parser.add_option("-c", "--continuous",
		action="store_true", dest="continuous", default=False,
		help="starts interface with 'continuous' listen enabled")

	parser.add_option("-o", "--override",
		action="store_true", dest="override", default=False,
		help="override config file with command line options")

	parser.add_option("-H", "--history", type="int",
		action="store", dest="history",
		help="number of commands to store in history file")

	parser.add_option("-m", "--microphone", type="int",
		action="store", dest="microphone", default=None,
		help="Audio input card to use (if other than system default)")

	parser.add_option("--valid-sentence-command",  type="string", dest="valid_sentence_command",
		action='store',
		help="command to run when a valid sentence is detected")

	parser.add_option( "--invalid-sentence-command",  type="string", dest="invalid_sentence_command",
		action='store',
		help="command to run when an invalid sentence is detected")

	(options, args) = parser.parse_args()
	#make our blather object
	blather = Blather(options)
	#init gobject threads
	gobject.threads_init()
	#we want a main loop
	main_loop = gobject.MainLoop()
	#handle sigint
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	#run the blather
	blather.run()
	#start the main loop

	try:
		main_loop.run()
	except:
		print "time to quit"
		main_loop.quit()
		sys.exit()

