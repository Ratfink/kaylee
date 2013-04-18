#!/usr/bin/env python2
import sys
import signal
import gobject
import os.path
import subprocess
from Recognizer import Recognizer

#where are the files?
conf_dir = os.path.expanduser("~/.config/blather")
lang_dir = os.path.join(conf_dir, "language")
command_file = os.path.join(conf_dir, "commands")
strings_file = os.path.join(conf_dir, "sentences.corpus")
lang_file = os.path.join(lang_dir,'lm')
dic_file = os.path.join(lang_dir,'dic')
#make the lang_dir if it doesn't exist
if not os.path.exists(lang_dir):
	os.makedirs(lang_dir)

class Blather:
	def __init__(self):
		self.continuous_listen = False
		self.commands = {}
		self.read_commands()
		self.recognizer = Recognizer(lang_file, dic_file)
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
						self.commands[key.strip()] = value.strip()
						strings.write( key.strip()+"\n")
		#close the strings file
		strings.close()
	
	
	def recognizer_finished(self, recognizer, text):
		#is there a matching command?
		if self.commands.has_key( text ):
			cmd = self.commands[text]
			print cmd
			subprocess.call(cmd, shell=True)
		else:
			print "no matching command"
		#if there is a UI and we are not continuous listen
		if self.ui:
			if not self.continuous_listen:
				#stop listening
				self.recognizer.pause()
			#let the UI know that there is a finish
			self.ui.finished(text)
	
	def run(self, args):
		#TODO check for UI request
		#is there an arg?
		if len(args) > 1:
			if args[1] == "-qt":
				#import the ui from qt
				from QtUI import UI
			elif args[1] == "-gtk":
				from GtkUI import UI
			else:
				print "no GUI defined"
				sys.exit()
			self.ui = UI(args)
			self.ui.connect("command", self.process_command)
			self.ui.run()
		else:
			blather.recognizer.listen()	

	def process_command(self, UI, command):
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
		
if __name__ == "__main__":
	#make our blather object
	blather = Blather()
	#init gobject threads
	gobject.threads_init()
	#we want a main loop
	main_loop = gobject.MainLoop()
	#run the blather
	blather.run(sys.argv)
	#start the main loop
	try:
		main_loop.run()
	except:
		main_loop.quit()
		sys.exit()
	
