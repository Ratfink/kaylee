#!/usr/bin/env python2
import pygst
pygst.require('0.10')
import gst
import subprocess
import os.path
import time
import gobject

#define some global variables
this_dir = os.path.dirname( os.path.abspath(__file__) )
lang_dir = os.path.join(this_dir, "language")
command_file = os.path.join(this_dir, "commands")
strings_file = os.path.join(this_dir, "sentences.corpus")

class TTS(gobject.GObject):
	__gsignals__ = {
		'finished' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
	}
	def __init__(self):
		gobject.GObject.__init__(self)
		self.commands = {}
		#build the pipeline
		cmd = 'autoaudiosrc ! audioconvert ! audioresample ! vader name=vad ! pocketsphinx name=asr ! appsink sync=false'
		self.pipeline=gst.parse_launch( cmd )
		#get the Auto Speech Recognition piece
		asr=self.pipeline.get_by_name('asr')
		asr.connect('result', self.result)
		asr.set_property('lm', os.path.join(lang_dir, 'lm'))
		asr.set_property('dict', os.path.join(lang_dir, 'dic'))
		asr.set_property('configured', True)
		#get the Voice Activity DEtectoR
		self.vad = self.pipeline.get_by_name('vad')
		self.vad.set_property('auto-threshold',True)
		self.read_commands()
		#init gobject threads
		gobject.threads_init()
		
	def listen(self):
		self.pipeline.set_state(gst.STATE_PLAYING)
		
	def pause(self):
		self.vad.set_property('silent', True)
		self.pipeline.set_state(gst.STATE_PAUSED)

	def result(self, asr, text, uttid):
		#emit finished
		self.emit("finished", True)
		print text
		#is there a matching command?
		if self.commands.has_key( text ):
			cmd = self.commands[text]
			print cmd
			subprocess.call(cmd, shell=True)
		else:
			print "no matching command"
		
	def read_commands(self):
		#read the.commands file
		file_lines = open(command_file)
		strings = open(strings_file, "w")
		for line in file_lines:
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

if __name__ == "__main__":
	tts = TTS()
	tts.listen()
	main_loop = gobject.MainLoop()
	#start the main loop
	try:
		main_loop.run()
	except:
		main_loop.quit()
	


