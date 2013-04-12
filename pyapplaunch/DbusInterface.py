from PyQt4.QtCore import *
import math
import dbus
import dbus.service
from dbus.mainloop.qt import DBusQtMainLoop
 
G_BUS_NAME = "org.latticepoint.projects.pyapplaunch"
G_MAIN_BUS_OBJECT_NAME="/pyapplaunch"
 
class DbusInterface (dbus.service.Object):
	def __init__ (self, mainWindow):
		self.mainWindow = mainWindow
		
		DBusQtMainLoop (set_as_default = True)
			
		busName = dbus.service.BusName (G_BUS_NAME, bus = dbus.SessionBus())
		dbus.service.Object.__init__ (self, busName, G_MAIN_BUS_OBJECT_NAME)

	@dbus.service.method (G_BUS_NAME)
	def show (self): self.mainWindow.showWindow()
	
	@dbus.service.method (G_BUS_NAME)
	def hide (self): self.mainWindow.hideWindow()

	@dbus.service.method (G_BUS_NAME)
	def toggle (self): self.mainWindow.toggleWindow()
	
	#@dbus.service.method (G_BUS_NAME, in_signature = 'dd', out_signature = 'd')
	#def add(self, a, b): return a+b
