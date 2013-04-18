#!/usr/bin/env python2
import sys
import signal
import gobject
# Qt stuff
from PySide.QtCore import Signal, Qt
from PySide.QtGui import QApplication, QWidget, QMainWindow, QVBoxLayout
from PySide.QtGui import QLabel, QPushButton, QCheckBox

class UI(gobject.GObject):
	__gsignals__ = {
		'command' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))
	}
	
	def __init__(self,args):
		gobject.GObject.__init__(self)
		#start by making our app
		self.app = QApplication(args)
		#make a window
		self.window = QMainWindow()
		#give the window a name
		self.window.setWindowTitle("BlatherQt")
		center = QWidget()
		self.window.setCentralWidget(center)
		
		layout = QVBoxLayout()
		center.setLayout(layout)
		#make a listen/stop button
		self.lsbutton = QPushButton("Listen")
		layout.addWidget(self.lsbutton)
		#make a continuous button
		self.ccheckbox = QCheckBox("Continuous Listen")
		layout.addWidget(self.ccheckbox)
		
		#connect the buttonsc
		self.lsbutton.clicked.connect(self.lsbutton_clicked)
		self.ccheckbox.clicked.connect(self.ccheckbox_clicked)
	
	def recognizer_finished(self, x, y):
		if self.ccheckbox.isChecked():
			pass
		else:
			self.lsbutton_stopped()
			
			
	def ccheckbox_clicked(self):
		checked = self.ccheckbox.isChecked()
		if checked:
			#disable lsbutton
			self.lsbutton.setEnabled(False)
			self.lsbutton_stopped()
			self.emit('command', "continuous_listen")
		else:
			self.lsbutton.setEnabled(True)
			self.emit('command', "continuous_stop")
	
	def lsbutton_stopped(self):
		self.lsbutton.setText("Listen")
		
	def lsbutton_clicked(self):
		val = self.lsbutton.text()
		print val
		if val == "Listen":
			self.emit("command", "listen")
			self.lsbutton.setText("Stop")
		else:
			self.lsbutton_stopped()
			self.emit("command", "stop")
			
	def run(self):
		self.window.show()
		self.app.exec_()
	
	def finished(self, text):
		print text
		#if the continuous isn't pressed
		if not self.ccheckbox.isChecked():
			self.lsbutton_stopped()
		
	def quit(self):
		#sys.exit()
		pass
