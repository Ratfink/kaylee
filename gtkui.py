# This is part of Kaylee
# -- this code is licensed GPLv3
# Copyright 2013 Jezra
# Copyright 2015 Clayton G. Hobbs

import sys
from gi.repository import GObject
# Gtk
from gi.repository import Gtk, Gdk

class UI(GObject.GObject):
    __gsignals__ = {
        'command' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))
    }

    def __init__(self, args, continuous):
        GObject.GObject.__init__(self)
        self.continuous = continuous
        # Make a window
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        # Give the window a name
        self.window.set_title("Kaylee")
        self.window.set_resizable(False)

        layout = Gtk.VBox()
        self.window.add(layout)
        # Make a listen/stop button
        self.lsbutton = Gtk.Button("Listen")
        layout.add(self.lsbutton)
        # Make a continuous button
        self.ccheckbox = Gtk.CheckButton("Continuous Listen")
        layout.add(self.ccheckbox)

        # Connect the buttons
        self.lsbutton.connect("clicked", self.lsbutton_clicked)
        self.ccheckbox.connect("clicked", self.ccheckbox_clicked)

        # Add a label to the UI to display the last command
        self.label = Gtk.Label()
        layout.add(self.label)

        # Create an accellerator group for this window
        accel = Gtk.AccelGroup()
        # Add the ctrl+q to quit
        accel.connect(Gdk.keyval_from_name('q'), Gdk.ModifierType.CONTROL_MASK,
                Gtk.AccelFlags.VISIBLE, self.accel_quit)
        # Lock the group
        accel.lock()
        # Add the group to the window
        self.window.add_accel_group(accel)

    def ccheckbox_clicked(self, widget):
        checked = self.ccheckbox.get_active()
        self.lsbutton.set_sensitive(not checked)
        if checked:
            self.lsbutton_stopped()
            self.emit('command', "continuous_listen")
            self.set_icon_active()
        else:
            self.emit('command', "continuous_stop")
            self.set_icon_inactive()

    def lsbutton_stopped(self):
        self.lsbutton.set_label("Listen")

    def lsbutton_clicked(self, button):
        val = self.lsbutton.get_label()
        if val == "Listen":
            self.emit("command", "listen")
            self.lsbutton.set_label("Stop")
            # Clear the label
            self.label.set_text("")
            self.set_icon_active()
        else:
            self.lsbutton_stopped()
            self.emit("command", "stop")
            self.set_icon_inactive()

    def run(self):
        # Set the default icon
        self.set_icon_inactive()
        self.window.show_all()
        if self.continuous:
            self.set_icon_active()
            self.ccheckbox.set_active(True)

    def accel_quit(self, accel_group, acceleratable, keyval, modifier):
        self.emit("command", "quit")

    def delete_event(self, x, y):
        self.emit("command", "quit")

    def finished(self, text):
        # If the continuous isn't pressed
        if not self.ccheckbox.get_active():
            self.lsbutton_stopped()
            self.set_icon_inactive()
        self.label.set_text(text)

    def set_icon_active_asset(self, i):
        self.icon_active = i

    def set_icon_inactive_asset(self, i):
        self.icon_inactive = i

    def set_icon_active(self):
        Gtk.Window.set_default_icon_from_file(self.icon_active)

    def set_icon_inactive(self):
        Gtk.Window.set_default_icon_from_file(self.icon_inactive)
