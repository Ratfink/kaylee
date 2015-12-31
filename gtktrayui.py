# This is part of Kaylee
# -- this code is licensed GPLv3
# Copyright 2015 Clayton G. Hobbs
# Portions Copyright 2013 Jezra

import sys
import gi
from gi.repository import GObject
# Gtk
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class UI(GObject.GObject):
    __gsignals__ = {
        'command' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))
    }
    idle_text = "Kaylee - Idle"
    listening_text = "Kaylee - Listening"

    def __init__(self, args, continuous):
        GObject.GObject.__init__(self)
        self.continuous = continuous

        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_title("Kaylee")
        self.statusicon.set_name("Kaylee")
        self.statusicon.set_tooltip_text(self.idle_text)
        self.statusicon.set_has_tooltip(True)
        self.statusicon.connect("activate", self.continuous_toggle)
        self.statusicon.connect("popup-menu", self.popup_menu)

        self.menu = Gtk.Menu()
        self.menu_listen = Gtk.MenuItem('Listen')
        self.menu_continuous = Gtk.CheckMenuItem('Continuous')
        self.menu_quit = Gtk.MenuItem('Quit')
        self.menu.append(self.menu_listen)
        self.menu.append(self.menu_continuous)
        self.menu.append(self.menu_quit)
        self.menu_listen.connect("activate", self.toggle_listen)
        self.menu_continuous.connect("toggled", self.toggle_continuous)
        self.menu_quit.connect("activate", self.quit)
        self.menu.show_all()

    def continuous_toggle(self, item):
        checked = self.menu_continuous.get_active()
        self.menu_continuous.set_active(not checked)

    def toggle_continuous(self, item):
        checked = self.menu_continuous.get_active()
        self.menu_listen.set_sensitive(not checked)
        if checked:
            self.menu_listen.set_label("Listen")
            self.emit('command', "continuous_listen")
            self.statusicon.set_tooltip_text(self.listening_text)
            self.set_icon_active()
        else:
            self.set_icon_inactive()
            self.statusicon.set_tooltip_text(self.idle_text)
            self.emit('command', "continuous_stop")

    def toggle_listen(self, item):
        val = self.menu_listen.get_label()
        if val == "Listen":
            self.set_icon_active()
            self.emit("command", "listen")
            self.menu_listen.set_label("Stop")
            self.statusicon.set_tooltip_text(self.listening_text)
        else:
            self.set_icon_inactive()
            self.menu_listen.set_label("Listen")
            self.emit("command", "stop")
            self.statusicon.set_tooltip_text(self.idle_text)

    def popup_menu(self, item, button, time):
        self.menu.popup(None, None, Gtk.StatusIcon.position_menu, item, button, time)

    def run(self):
        # Set the icon
        self.set_icon_inactive()
        if self.continuous:
            self.menu_continuous.set_active(True)
            self.set_icon_active()
        else:
            self.menu_continuous.set_active(False)
        self.statusicon.set_visible(True)

    def quit(self, item):
        self.statusicon.set_visible(False)
        self.emit("command", "quit")

    def finished(self, text):
        if not self.menu_continuous.get_active():
            self.menu_listen.set_label("Listen")
            self.set_icon_inactive()
            self.statusicon.set_tooltip_text(self.idle_text)

    def set_icon_active_asset(self, i):
        self.icon_active = i

    def set_icon_inactive_asset(self, i):
        self.icon_inactive = i

    def set_icon_active(self):
        self.statusicon.set_from_file(self.icon_active)

    def set_icon_inactive(self):
        self.statusicon.set_from_file(self.icon_inactive)
