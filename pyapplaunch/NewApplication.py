from PyQt4.QtCore import *
from PyQt4 import QtGui

import re

from RadioManagement import RadioManagement

class NewApplication (QtGui.QDialog, RadioManagement):
	def __init__ (self, appDefaultDetails, execManager):
		super (NewApplication, self).__init__()

		self.execManager = execManager

		self.radioCol = 0
		self.gridGridCol = 1
		self.gridLabelLabelCol = 0
		self.gridLabelCol = 1
		self.paramReqCol = 2

		self.initUI()

		self.appDetails = appDefaultDetails.copy()

		self.setValues (appDefaultDetails)

	def initUI (self):
		vbox = QtGui.QVBoxLayout()
		grid = QtGui.QGridLayout()

		vbox.addLayout (grid)

		# Set window properties
		self.setGeometry (300, 300, 290, 150)
		self.setWindowTitle ("Add New Script")
		self.setLayout (vbox)

		# Setup widgets.

		# Name
		self.nameLabel = QtGui.QLabel ("Name", self)
		grid.addWidget (self.nameLabel, 0, 0)

		self.name = QtGui.QLineEdit (self)
		grid.addWidget (self.name, 0, 1)

		# Command
		self.nameLabel = QtGui.QLabel ("Command", self)
		grid.addWidget (self.nameLabel, 1, 0)

		self.command = QtGui.QLineEdit (self)
		grid.addWidget (self.command, 1, 1)

		self.cmdBtn = QtGui.QPushButton ("...", self)
		moreFilesWidth = self.cmdBtn.fontMetrics().boundingRect ("...").width()
		self.cmdBtn.setMaximumWidth (moreFilesWidth + 15)
		grid.addWidget (self.cmdBtn, 1, 2)
		self.cmdBtn.clicked.connect (self.cmdBtnClicked)

		# Execution delegate
		label = QtGui.QLabel ("Using", self)
		grid.addWidget (label, 2, 0)

		execBox = QtGui.QHBoxLayout()
		grid.addLayout (execBox, 2, 1)

		self.execDelegate = QtGui.QComboBox (self)
		#grid.addWidget (self.execDelegate, 2, 1)
		execBox.addWidget (self.execDelegate)
		execBox.setStretch (0, 1) # combo box get largest share of space.

		self.execEditBtn = QtGui.QPushButton ("configure", self)
		self.execEditBtn.clicked.connect (self.execEditBtnClicked)
		execBox.addWidget (self.execEditBtn)

		self.populateUsingComboBox()

		# A horizontal rule.
		line = QtGui.QFrame (self)
		line.setFrameShape (QtGui.QFrame.HLine)
		line.setFrameShadow (QtGui.QFrame.Sunken)
		vbox.addWidget (line)

		# "Parameters" label.
		label = QtGui.QLabel ("Parameters", self)
		vbox.addWidget (label, 0, Qt.Alignment (4))

		font = QtGui.QFont (self)
		font.setPointSize (16)
		label.setFont (font)

		# Parameter box.
		self.paramLayout = QtGui.QGridLayout()
		vbox.addLayout (self.paramLayout)

		# grid column stretches most
		self.paramLayout.setColumnStretch (1, 1)

		RadioManagement.__init__ (self, self.radioCol, self.paramLayout)

		self.initDelAndMovButtons (vbox)

		# Insert "new" button start of edit buttons.
		self.newParamBtn = QtGui.QPushButton ("New &Param", self)
		self.newParamBtn.clicked.connect (self.newParamBtnClicked)
		self.editHBox.insertWidget (0, self.newParamBtn)

		# A horizontal rule.
		line = QtGui.QFrame (self)
		line.setFrameShape (QtGui.QFrame.HLine)
		line.setFrameShadow (QtGui.QFrame.Sunken)
		vbox.addWidget (line)

		controlButtonLayout = QtGui.QHBoxLayout()
		vbox.addLayout (controlButtonLayout)

		# Control buttons.
		self.cancelBtn = QtGui.QPushButton ("&cancel", self)
		controlButtonLayout.addWidget (self.cancelBtn)
		self.connect (self.cancelBtn, SIGNAL ('clicked()'), SLOT ('reject()'))

		self.okBtn = QtGui.QPushButton ("&ok", self)
		self.okBtn.setDefault(True)
		controlButtonLayout.addWidget (self.okBtn)
		self.okBtn.clicked.connect (self.okBtnClicked)

		self.show()

	def setValues (self, values):
		if "name" in values:
			self.name.setText (values ["name"])
		if "command" in values:
			self.command.setText (values ["command"])
		if "exec_with" in values:
			comboItems = self.execManager.getDelegates().keys()

			if values ["exec_with"] in comboItems:
				comboIndex = comboItems.index (values ["exec_with"])
				self.execDelegate.setCurrentIndex (comboIndex)

		if "use_sudo" in values:
			pass

		# Set the parameters.
		if "params" in values:
			for param in values ["params"]:
				self.addParameter (param)

	def populateUsingComboBox (self):
		self.execDelegate.clear()
		self.execDelegate.addItems (self.execManager.getDelegates().keys())

	def cmdBtnClicked (self):
		self.showGetFileDialog (self.command)

	def okBtnClicked (self):
		error = QtGui.QErrorMessage(self)

		# Check that acceptible values were selected.
		if len (self.name.text()) == 0:
			error.showMessage ("No name selected!")
			error.exec_()
			return

		if len (self.command.text()) == 0:
			error.showMessage ("No command selected!")
			error.exec_()
			return

		retval, errMsg = self.checkAllParamsAreValid()
		if retval == False:
			error.showMessage (errMsg)
			error.exec_()
			return

		self.accept()

	def showGetFileDialog (self, textTarget):
		text = QtGui.QFileDialog.getOpenFileName (self, 'command to run')

		if len (text) != 0:
			textTarget.setText (str (text))

	def addParameter (self, defaultValues = {}):
		rowNum = self.getRowCount() + 1 # +1 to offset to the next free row.

		# Add the number
		self.buildRow (self.paramLayout, rowNum)

		# Second grid layout for we will need multiple lines
		gridLayout = QtGui.QGridLayout()
		self.paramLayout.addLayout (gridLayout, rowNum, self.gridGridCol)

		# Edit box for parameter's name
		label = QtGui.QLabel ("Label:", self)
		gridLayout.addWidget (label, 0, self.gridLabelLabelCol)

		paramLabel = QtGui.QLineEdit (self)
		gridLayout.addWidget (paramLabel, 0, self.gridLabelCol)
		self.setDefaultValue (paramLabel, defaultValues, "name")

		# Parameter required checkbox
		paramRequired = QtGui.QCheckBox ("Required?", self)
		gridLayout.addWidget (paramRequired, 0, self.paramReqCol)
		self.setDefaultValue (paramRequired, defaultValues, "required")

		# Edit box for parameter's default value.
		label = QtGui.QLabel ("Default:", self)
		gridLayout.addWidget (label, 1, self.gridLabelLabelCol)

		defaultVal = QtGui.QLineEdit (self)
		gridLayout.addWidget (defaultVal, 1, self.gridLabelCol)
		self.setDefaultValue (defaultVal, defaultValues, "default")

		# Show file dialog button checkbox.
		showDialog = QtGui.QCheckBox ("file selector?", self)
		gridLayout.addWidget (showDialog, 1, self.paramReqCol)
		self.setDefaultValue (showDialog, defaultValues, "file_selector")

		# We'll also add the symbol needed to know where to susbsitute the
		# parameter, if it's not already in it's place.
		if not self.isParamSymbolPresent (rowNum):
			self.command.setText (self.command.text() + " %" + str (rowNum))

	def checkAllParamsAreValid (self):
		params = self.returnParams()
		# The only required value for a paramter is a label (name).
		for index, param in enumerate (params):
			# Check the parameter has a name.
			if param ["name"] == "":
				return False, "No name for param #" + str (param ["slot"])

			if not self.isParamSymbolPresent (index + 1):
				return False, "Missing parameter symbol '%" + \
					str (index + 1) + "' in command!"

		return True, ""

	def isParamSymbolPresent (self, paramNumber):
		# Check that a valid place marker is in "command" edit box.
		paramCheck = re.search ("(?:[^%]|%%+|^)%" + \
			str (paramNumber) + "(?:[^0-9]|$)", self.command.text())

		if paramCheck == None:
			return False
		else:
			return True

	def setDefaultValue (self, widget, defaultValues, key):
		if not key in defaultValues:
			return

		# Are we processing a checkbox?
		if type (widget) == QtGui.QLineEdit:
			widget.setText (defaultValues [key])
		elif type (widget) == QtGui.QCheckBox:
			value = defaultValues [key]
			# The parameter type could be either bool-
			if type (value) == bool:
				widget.setChecked (value)
			else:
				# -Or a string containing "True" or "False".
				if (value == "True"):
					widget.setChecked (True)
				else:
					widget.setChecked (False)

	def returnParams (self):
		params = []

		for rowCount in self.getRowRange():
			param = {}
			paramGrid = self.paramLayout.itemAtPosition (rowCount, self.gridGridCol)

			widget = paramGrid.itemAtPosition (0, self.gridLabelCol).widget()
			param ["name"] = widget.text()
			widget = paramGrid.itemAtPosition (0, self.paramReqCol).widget()
			param ["required"] = widget.isChecked()
			widget = paramGrid.itemAtPosition (1, self.gridLabelCol).widget()
			param ["default"] = widget.text()
			widget = paramGrid.itemAtPosition (1, self.paramReqCol).widget()
			param ["file_selector"] = widget.isChecked()
			param ["slot"] = rowCount

			params.append (param)

		return params

	def returnNewAppDetails (self):
		self.appDetails ["name"] = str (self.name.text())
		self.appDetails ["command"] = str (self.command.text())

		if not "use_sudo" in self.appDetails:
			self.appDetails ["use_sudo"] = str (False)
		if not "slot" in self.appDetails:
			self.appDetails ["slot"] = 0

		# We don't use this dialog for creating groups.
		self.appDetails ["is_group"] = "False"
		self.appDetails ["exec_with"] = str (self.execDelegate.currentText())

		self.appDetails ["params"] = self.returnParams()

		return self.appDetails

	def execEditBtnClicked (self):
		self.execManager.editDelegates()
		self.populateUsingComboBox()

	def newParamBtnClicked (self):
		self.addParameter()
