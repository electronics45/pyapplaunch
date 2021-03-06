from PyQt4.QtCore import *
from PyQt4 import QtGui

import os.path
import pickle
from collections import OrderedDict

import ConfigManager
from RadioManagement import RadioManagement

class ExecutionDelegateManager (QtGui.QWidget):
	delegateNameChanged = pyqtSignal (str, str)

	def __init__ (self, configManager):
		QtGui.QWidget.__init__(self, None)

		self.configManager = configManager
		self.loadDelegateList ()

	def loadDelegateList (self):
		self.delegates = self.configManager.getConfigSection ("execDelegates")

		# If the list is empty, add "bash" so that it is not empty.
		if len (self.delegates) == 0:
			self.delegates = {"xterm":"xterm -e"}

	def saveDelegateList (self):

		self.configManager.setSection ("execDelegates", self.delegates)
		self.configManager.writeConfigFile()

	def editDelegates (self):
		dialog = EditExecDelegateDialog (self.delegates)

		dialog.delegateNameChanged.connect (self.delegateNameChanged.emit)

		if not dialog.exec_():
			return False

		# Retrieve and store
		self.delegates = dialog.getDelegates()

		#print self.delegates

		self.saveDelegateList ()

		return True

	def getDelegates (self):
		return self.delegates

class EditExecDelegateDialog (QtGui.QDialog, RadioManagement):
	delegateNameChanged = pyqtSignal (str, str)

	def __init__ (self, defaultDelegates = {}):
		super (EditExecDelegateDialog, self).__init__()

		# A signal to noftify of when an execution delegate's name has been
		# changed.
		#self.delegateNameChanged = pyqtSignal (unicode, unicode)

		self.radioCol = 0
		self.gridGridCol = 1

		self.grdLblCol = 0
		self.grdTxtCol = 1
		self.grdChkCol = 2

		self.initUI()

		# Load all default delegates
		for delegateName in defaultDelegates.keys():
			self.addExecDelegate (delegateName, defaultDelegates [delegateName])

		# We'll need to save the defaults for later comparision.
		self.defaultDelegates = defaultDelegates
	
	def initUI (self):
		vbox = QtGui.QVBoxLayout()
		self.grid = QtGui.QGridLayout()

		vbox.addLayout (self.grid)

		RadioManagement.__init__ (self, self.radioCol, self.grid)

		# Set window properties
		self.setGeometry (300, 300, 290, 150)
		self.setWindowTitle ("Manage Execution Delegates")
		self.setLayout (vbox)

		self.initDelAndMovButtons (vbox)

		# Insert "new" button start of edit buttons.
		self.newParamBtn = QtGui.QPushButton ("New &Delegate", self)
		self.newParamBtn.clicked.connect (self.newDelegateButtonClicked)
		self.editHBox.insertWidget (0, self.newParamBtn)

		controlButtonLayout = QtGui.QHBoxLayout()
		vbox.addLayout (controlButtonLayout)

		# O.K. and cancel buttons.
		button = QtGui.QPushButton ("&cancel", self)
		controlButtonLayout.addWidget (button)
		self.connect (button, SIGNAL ('clicked()'), SLOT ('reject()'))

		button = QtGui.QPushButton ("&O.K.", self)
		button.setDefault(True)
		controlButtonLayout.addWidget (button)
		button.clicked.connect (self.okBtnClicked)

	def addExecDelegate (self, defaultName = None, defaultCommand = None):
		rowNum = self.getRowCount() + 1 # +1 to offset to the next free row.

		# Add the number
		self.buildRow (self.grid, rowNum)

		# Second grid layout for we will need multiple lines
		gridLayout = QtGui.QGridLayout()
		self.grid.addLayout (gridLayout, rowNum, self.gridGridCol)

		# Edit box for parameter's name
		label = QtGui.QLabel ("Label:", self)
		gridLayout.addWidget (label, 0, self.grdLblCol)

		textBox = QtGui.QLineEdit (self)
		gridLayout.addWidget (textBox, 0, self.grdTxtCol)
		if defaultName:
			textBox.setText (defaultName)
			# This is a hack which I'm using to assign arbitrary text to the
			# widget, since there does not seem to be any way to associate user
			# data with a widget.  If anyone has less ugly way to do this,
			# (including restructuring the code) please let me know.
			textBox.setAccessibleName (defaultName)

		# Command with which to execute the applications.
		label = QtGui.QLabel ("Command:", self)
		gridLayout.addWidget (label, 1, self.grdLblCol)

		textBox = QtGui.QLineEdit (self)
		gridLayout.addWidget (textBox, 1, self.grdTxtCol)
		if defaultCommand:
			textBox.setText (defaultCommand)

	def storeParameters (self):
		delegates = OrderedDict ({})
		changedNames = {}

		# Iterate over every entry.
		for entryNum in self.getRowRange():
			layoutItem = self.gridLayout.itemAtPosition (entryNum, 1)

			if layoutItem == None:
				continue

			layout = layoutItem.layout()

			# Iterate over every attribute of this entry.
			#for attribNum in range (layout.getRowCount()):
			name = str (layout.itemAtPosition (0,
				self.grdTxtCol).widget().text())
			cmd = str (layout.itemAtPosition (1,
				self.grdTxtCol).widget().text())

			# This is a hack which I'm using to assign arbitrary text to the
			# widget, since there does not seem to be any way to associate user
			# data with a widget.  If anyone has less ugly way to do this,
			# (including restructuring the code) please let me know.
			previousName = str (layout.itemAtPosition (0,
				self.grdTxtCol).widget().accessibleName ())

			if len (name) == 0:
				self.warn ("Entry '" + str (entryNum) + "' does not have name!")
				return False, delegates

			# If an execution delegate with this name already exists.
			if name in delegates:
				#self.warnNameError (name)
				self.warn ("Entry '" + str (entryNum) + "' has a duplicate name!")
				return False, delegates

			if len (previousName) != 0 and previousName != name:
				# Keep track of these name changes for later.
				changedNames [previousName] = name

			delegates [name] = cmd

		self.delegates = delegates.copy()

		# All parameters have now been verified and saved.  It's safe to
		# notify about all names which have changed.
		for oldName in changedNames.keys():
			self.delegateNameChanged.emit (oldName, changedNames [oldName])

		return True, delegates

	def areParamsOk (self):
		pass

	def getDelegates (self):
		return self.delegates

	def warn (self, message):
		error = QtGui.QErrorMessage (self)
		error.showMessage (message)
		error.exec_()

	def newDelegateButtonClicked (self):
		self.addExecDelegate()

	def okBtnClicked (self):
		# Check that all "required" parameters are filled in.
		ok,params = self.storeParameters()
		if ok:
			self.accept()
