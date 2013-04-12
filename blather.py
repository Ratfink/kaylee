#!/usr/bin/env python2
import sys
import signal
import gobject
# Qt stuff
from PySide.QtCore import Signal, Qt
from PySide.QtGui import QApplication, QWidget, QMainWindow, QVBoxLayout
from PySide.QtGui import QLabel, QPushButton, QCheckBox
from Recognizer import Recognizer

class Blather:
	def __init__(self):
		self.recognizer = Recognizer();
		self.recognizer.connect('finished',self.recognizer_finished)
		#make a window
		self.window = QMainWindow()
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
			self.recognizer.listen()
		else:
			self.lsbutton.setEnabled(True)
	
	def lsbutton_stopped(self):
		self.recognizer.pause()
		self.lsbutton.setText("Listen")
		
	def lsbutton_clicked(self):
		val = self.lsbutton.text()
		print val
		if val == "Listen":
			self.recognizer.listen()
			self.lsbutton.setText("Stop")
		else:
			self.lsbutton_stopped()
			
	def run(self):
		self.window.show()
		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	b = Blather()
	b.run()
	
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	#start the app running
	sys.exit(app.exec_())
	
