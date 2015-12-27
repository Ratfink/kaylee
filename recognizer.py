# This is part of Kaylee
# -- this code is licensed GPLv3
# Copyright 2013 Jezra
# Copyright 2015 Clayton G. Hobbs

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
GObject.threads_init()
Gst.init(None)
import os.path
import sys

# Define some global variables
this_dir = os.path.dirname( os.path.abspath(__file__) )


class Recognizer(GObject.GObject):
    __gsignals__ = {
        'finished' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))
    }

    def __init__(self, language_file, dictionary_file, src = None):
        GObject.GObject.__init__(self)
        self.commands = {}
        if src:
            audio_src = 'alsasrc device="hw:%d,0"' % (src)
        else:
            audio_src = 'autoaudiosrc'

        # Build the pipeline
        cmd = audio_src+' ! audioconvert ! audioresample ! pocketsphinx name=asr ! appsink sync=false'
        try:
            self.pipeline=Gst.parse_launch( cmd )
        except Exception as e:
            print(e.message)
            print("You may need to install gstreamer1.0-pocketsphinx")
            raise e

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()

        # Get the Auto Speech Recognition piece
        asr=self.pipeline.get_by_name('asr')
        bus.connect('message::element', self.result)
        asr.set_property('lm', language_file)
        asr.set_property('dict', dictionary_file)
        asr.set_property('configured', True)

    def listen(self):
        self.pipeline.set_state(Gst.State.PLAYING)

    def pause(self):
        self.pipeline.set_state(Gst.State.PAUSED)

    def result(self, bus, msg):
        msg_struct = msg.get_structure()
        # Ignore messages that aren't from pocketsphinx
        msgtype = msg_struct.get_name()
        if msgtype != 'pocketsphinx':
            return

        # If we have a final command, send it for processing
        command = msg_struct.get_string('hypothesis')
        if command != '' and msg_struct.get_boolean('final')[1]:
            self.emit("finished", command)
