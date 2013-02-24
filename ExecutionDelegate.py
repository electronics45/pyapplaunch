from PyQt4.QtCore import *
from PyQt4 import QtGui

import os.path
import pickle
from collections import OrderedDict

from radioManagement import radioManagement

class ExecutionDelegateManager ():
	def __init__ (self):
		self.pylaunchDir = os.path.dirname (os.path.abspath(__file__))
		self.defaultDelegateListPath = os.path.join (self.pylaunchDir, "exec_delegates.config")

		self.loadDelegateList (self.defaultDelegateListPath)

	def loadDelegateList (self, listPath):
		
		if os.path.exists (listPath):
			with open (listPath, 'r') as fileHandle:
				#data = fileHandle.read()
				#self.delegates = ast.literal_eval (data)
				self.delegates = pickle.loads (fileHandle.read())
		else:
			# File does not exist.  We'll use an empty dictionary instead.
			self.delegates = {}

	def saveDelegateList (self, listPath):
		with open (listPath, 'w') as fileHandle:
			 pickle.dump (self.delegates, fileHandle)

	def editDelegates (self):
		dialog = EditExecDelegateDialog (self.delegates)

		if not dialog.exec_():
			return False

		# Retrieve and store
		self.delegates = dialog.getDelegates()

		self.saveDelegateList(self.defaultDelegateListPath)

		return True

class EditExecDelegateDialog (QtGui.QDialog, radioManagement):
	def __init__ (self, defaultDelegates = {}):
		super (EditExecDelegateDialog, self).__init__()

		self.radioCol = 0
		self.gridGridCol = 1

		self.grdLblCol = 0
		self.grdTxtCol = 1
		self.grdChkCol = 2

		self.initUI()

		# Load all default delegates
		for delegateName in defaultDelegates.keys():
			self.addExecDelegate (delegateName, defaultDelegates [delegateName])
	
	def initUI (self):
		vbox = QtGui.QVBoxLayout()
		self.grid = QtGui.QGridLayout()

		vbox.addLayout (self.grid)

		radioManagement.__init__ (self, self.radioCol, self.grid)

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
			#self.setDefaultValue (textBox, defaultValues, defaultName)
			textBox.setText (defaultName)

		## use sudo checkbox
		#paramRequired = QtGui.QCheckBox ("Sudo?", self)
		#gridLayout.addWidget (paramRequired, 0, self.grdChkCol)
		#self.setDefaultValue (paramRequired, defaultValues, "sudo")

		# Command with which to execute the applications.
		label = QtGui.QLabel ("Command:", self)
		gridLayout.addWidget (label, 1, self.grdLblCol)

		textBox = QtGui.QLineEdit (self)
		gridLayout.addWidget (textBox, 1, self.grdTxtCol)
		if defaultCommand:
			#self.setDefaultValue (textBox, defaultValues, defaultCommand)
			textBox.setText (defaultCommand)

	def storeParameters (self):
		delegates = OrderedDict ({})

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

			# If an execution delegate with this name already exists.
			if name in delegates:
				self.warnNameError (name)
				return False, delegates

			delegates [name] = cmd
			print delegates

		print delegates

		self.delegates = delegates.copy()

		return True, delegates

	def areParamsOk (self):
		pass

	#def setDefaultValue (self, widget, defaultValues, key):
		#if not key in defaultValues:
			#return

		## Are we processing a checkbox?
		#if type (widget) == QtGui.QLineEdit:
			#widget.setText (defaultValues [key])
		#elif type (widget) == QtGui.QCheckBox:
			#value = defaultValues [key]
			## The parameter type could be either bool-
			#if type (value) == bool:
				#widget.setChecked (value)
			#else:
				## -Or a string containing "True" or "False".
				#if (value == "True"):
					#widget.setChecked (True)
				#else:
					#widget.setChecked (False)

	def getDelegates (self):
		return self.delegates

	def newDelegateButtonClicked (self):
		self.addExecDelegate()

	def okBtnClicked (self):
		# Check that all "required" parameters are filled in.
		

		if self.storeParameters():#self.areParamsOk():
			self.accept()