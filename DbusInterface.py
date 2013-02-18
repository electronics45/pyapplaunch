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
	
	
	@dbus.service.method (G_BUS_NAME)#, in_signature = 'dd', out_signature = 'd')
	def show (self): self.mainWindow.show()
	
	@dbus.service.method (G_BUS_NAME)#, in_signature = 'dd', out_signature = 'd')
	def hide (self): self.mainWindow.hide()
	
	#@dbus.service.method (G_BUS_NAME, in_signature = 'dd', out_signature = 'd')
	#def add(self, a, b): return a+b
	
	#@dbus.service.method (G_BUS_NAME, in_signature = 'i', out_signature = 'i')
	#def factorial (self, n): return 1 if n <= 1 else n*self.factorial (n-1)
	
	#@dbus.service.method (G_BUS_NAME, in_signature = 'd', out_signature = 'd')
	#def sqrt (self, n): return math.sqrt (n)
	
	#@dbus.service.method (G_BUS_NAME, in_signature = 'd', out_signature = 'i')
	#def round (self, n): return round (n)
 
#DBusQtMainLoop (set_as_default = True)
#app = QCoreApplication([])
#interface = DbusAccess()
#app.exec_()