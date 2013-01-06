#! /usr/bin/python

from PyQt4.QtCore import *
from PyQt4 import QtGui
import signal
import sys
import os
import re
from functools import partial

#import xml.etree.cElementTree as xml

from radioManagement import radioManagement
from Tree import Tree

class MainWindow (QtGui.QMainWindow, radioManagement):
	def __init__ (self):
		QtGui.QMainWindow.__init__ (self)

		self.btnCol = 1
		self.radioCol = 0

		radioManagement.__init__ (self, self.radioCol)

		self.pylaunchDir = os.path.dirname (os.path.abspath(__file__))
		self.scriptDatabasePath = self.pylaunchDir + os.sep + "scripts.xml"

		self.tree = Tree (self.scriptDatabasePath)

		self.initUI()

		self.buildAppButtons()

	def initUI (self):
		QtGui.QShortcut (QtGui.QKeySequence ("Esc"), self, self.close)
		QtGui.QShortcut (QtGui.QKeySequence ("Ctrl+Q"), self, self.close)

		self.mainWidget = QtGui.QWidget (self) # dummy to contain the layout.
		self.setCentralWidget (self.mainWidget)

		#self.radioGroup = QtGui.QButtonGroup() # To store radio buttons.

		vbox = QtGui.QVBoxLayout()
		vbox.addStretch (1)

		# This layout will hold the script buttons once they're generated.
		self.buttonLayout = QtGui.QGridLayout()
		vbox.addLayout (self.buttonLayout)
		self.buttonLayout.setColumnStretch (self.btnCol, 1) # Btn column stretches most.

		# A horizontal rule.
		line = QtGui.QFrame (self)
		line.setFrameShape (QtGui.QFrame.HLine)
		line.setFrameShadow (QtGui.QFrame.Sunken)
		vbox.addWidget (line)

		# Insert the control buttons for managemnt of the generated buttons.
		self.initDelAndMovButtons (vbox)

		# Insert the edit button at the beginning of the edit box.
		button = QtGui.QPushButton ("&Edit", self)
		self.editHBox.insertWidget (0, button) # 0 = beginning of hbox.
		self.connect (button, SIGNAL ("clicked()"), self.editButtonClicked)

		newLayout = QtGui.QHBoxLayout()
		vbox.addLayout (newLayout)

		# The new script button.
		newAppBtn = QtGui.QPushButton ("&New Script", self)
		newLayout.addWidget (newAppBtn)
		self.connect (newAppBtn, SIGNAL ("clicked()"), self.showNewApp)

		# New Group button.
		newGroupBtn = QtGui.QPushButton ("New &Group", self)
		newLayout.addWidget (newGroupBtn)
		self.connect (newGroupBtn, SIGNAL ("clicked()"), self.newGroupBtnClicked)

		newGroupBtn.setShortcut (QtGui.QKeySequence ("1"))#, self, self.close))
		
		self.mainWidget.setLayout (vbox)
		self.setWindowTitle ("PyLaunch")

	def buildAppButtons (self, defaultSlot = None):
		row = 1

		#self.buttonNames = {}

		# First make sure all autogenerated buttons and such are removed.
		self.clearAppButtons()

		# Get the Application list.
		appList = self.tree.getApplications()

		for app in appList:
			self.buildRow (self.buttonLayout, row)

			# Set this radio button if it's slot matches that provided.
			if defaultSlot != None and app ["slot"] == defaultSlot:
				#radio.setChecked (True)
				self.setCheckedRadioButtonByRow (row)

			# Create the button.
			button = QtGui.QPushButton (app ["name"], self)
			self.buttonLayout.addWidget (button, row, self.btnCol)

			# Bind that button to a method which calls another method,
			# passing the name of the button being clicked to it.
			closure = partial (self.appButtonClicked, app ["name"])
			self.connect (button, SIGNAL ("clicked()"), closure)

			# We want a different colour for groups so we can tell them
			# appart.
			if app ["is_group"] == "True":
				self.setGroupButtonColour (button)

			row += 1

		# Build a button to take us up one level if we're not in the root context.
		if not self.tree.isRootContext():
			button = QtGui.QPushButton ("Go Up One Level", self)
			self.buttonLayout.addWidget (button, row, self.btnCol)
			self.connect (button, SIGNAL ("clicked()"), self.upLvlBtnClicked)
			#button.setStyleSheet("QPushButton {color:black; background-color: lightgrey;}")
			self.setGroupButtonColour (button)

	def clearAppButtons (self):
		self.clearGridLayout (self.buttonLayout)
		## This function removes all of the automatically generated
		## buttons and such from the layout.

		## Remove the radio buttons fromt "radioGroup".
		#for buttonEntry in self.radioGroup.buttons():
			#self.radioGroup.removeButton (buttonEntry)

		#for i in range (self.buttonLayout.rowCount()):
			#for j in range (self.buttonLayout.columnCount()):
				#widgetItem = self.buttonLayout.itemAtPosition(i, j)
				
				#if widgetItem != None:
					#widgetItem.widget().setParent(None)

	def getActiveAppName (self):
		#checkedButtonId = self.radioGroup.checkedId()

		#if checkedButtonId == -1:
			## No radio buttons are checked.
			#return None

		## Return the name of the button at "checkedButtonId"'s row.
		#button = self.buttonLayout.itemAtPosition (checkedButtonId, self.btnCol).widget()
		#return button.text()

		button = self.getWidgetAtCheckedRow (self.buttonLayout, self.btnCol)

		if button == None:
			return None

		return button.text()

	def getAppNameByRowNum (self, rowNum):
		item = self.buttonLayout.itemAtPosition (rowNum, self.btnCol)

		if item == None:
			# The item here does not exist.
			return None
		
		
		return item.widget().text()

	def createNewButton (self, editMethod, defaultDetails = {}):
		details = defaultDetails.copy()

		details, ok = self.editDetails (editMethod, details)

		if not ok:
			return

		# Set the slot to 1 past the number of app registered here.
		details ["slot"] = self.tree.getNumApps() + 1

		#self.tree.createNewGroup (groupDetails)
		self.tree.addApp (details)

		# Rebuild the buttons.
		self.buildAppButtons()

		# Save new configuration to disk.
		self.tree.writeTreeToDisk (self.scriptDatabasePath)

	def editDetails (self, editMethod, defaultDetails = {}):
		details = defaultDetails.copy()

		if "name" not in details:
			details ["name"] = ""
			originalName = ""
		else:
			originalName = defaultDetails ["name"]

		details, ok = editMethod (details)

		if not ok:
			return details, False

		# Check for name clashes.
		# Keep Retrying until the user succeeds.
		while self.tree.doesAppExistInCurrentContext (details ["name"]) == True:
			if details ["name"] == originalName:
				# Looks like the user decided to keep the original name.
				break

			error = QtGui.QErrorMessage(self)
			error.showMessage ("Script with that name already exists!")
			error.exec_()

			details, ok = editMethod (details)

			if not ok:
				return details, False  # User changed their mind.

		return details, True

	def editAppDetails (self, defaultDetails):
		newApp = NewApplication (defaultDetails)

		# Wait for the dialog to be closed/canceld/accepted/
		if not newApp.exec_():
			return defaultDetails, False
		
		returnDetails = newApp.returnNewAppDetails()

		return returnDetails, True

	def editGroupName (self, defaultDetails):
		details = defaultDetails.copy()

		details ["name"], ok = QtGui.QInputDialog.getText (self, 'New Group',
			'Enter a name for the new group:', QtGui.QLineEdit.Normal,
			details ["name"])

		# Check for a black name.  Assume they just don't want another group.
		if details ["name"] == "":
			return details, False

		#print details

		return details, ok

	def showNewApp (self):
		self.createNewButton (self.editAppDetails)

	def setGroupButtonColour (self, button):
		button.setStyleSheet("QPushButton {color:black; background-color: lightgrey;}")

	def newGroupBtnClicked (self):
		groupDetails = {}

		groupDetails ["is_group"] = "True"
		groupDetails ["children"] = ""

		self.createNewButton (self.editGroupName, groupDetails)

	def editButtonClicked (self):
		activeAppName = self.getActiveAppName()

		if activeAppName == None:
			print "No app selected!"
			return

		appDetails = self.tree.getAppDetails (self.getActiveAppName())

		if appDetails ["is_group"] == "False":
			newAppDetails, wasAccepted = self.editDetails (self.editAppDetails,
				appDetails)

			# Easiest thing to do now is delete the old app, and add a new one.
			self.tree.deleteApp (appDetails ["name"])
			self.tree.addApp (newAppDetails)

			#if not wasAccepted:
			## User changed their mind.  Don't want to edit after all.
			#return
		else:
			originalName = appDetails ["name"]

			newAppDetails, wasAccepted = self.editDetails (self.editGroupName,
				appDetails)

			self.tree.renameAndUpdateApp (originalName, appDetails)

		# Rebuild the buttons.
		self.buildAppButtons()

		# Commit changes to disk.
		self.tree.writeTreeToDisk (self.scriptDatabasePath)

	def deleteButtonClicked (self):
		activeAppName = self.getActiveAppName()

		if activeAppName == None:
			print "No app selected!"
			return

		self.tree.deleteApp (activeAppName)

		#self.buildAppButtons()
		self.deleteRow (self.buttonLayout, self.radioGroup.checkedId())

		# Commit changes to disk.
		self.tree.writeTreeToDisk (self.scriptDatabasePath)

	def moveUpButtonClicked (self):
		checkedRow = self.radioGroup.checkedId()
		swapRow = checkedRow - 1

		# First, retrieve the details of the active application.
		activeAppName = self.getActiveAppName()

		if activeAppName == None:
			print "No app selected!"
			return

		# Next, get the details of the application above this one.
		nextAppName = self.getAppNameByRowNum (swapRow)

		if nextAppName == None:
			print "App is already at highest position!"
			return

		# We're moveing this one up, so we want to swap with the app
		# above this one.
		activeApp = self.tree.getAppDetails (activeAppName)
		nextApp = self.tree.getAppDetails (nextAppName)

		print activeApp
		print nextApp
		self.swapSlots (activeApp, nextApp)

		# Use slot of moved app's (new) position for default checked radio.
		#self.buildAppButtons (activeApp ["slot"])
		self.swapRows (self.buttonLayout, checkedRow, swapRow)

		# Commit changes to disk.
		self.tree.writeTreeToDisk (self.scriptDatabasePath)

	def moveDownButtonClicked (self):
		# First, retrieve the details of the active application.
		activeAppName = self.getActiveAppName()

		if activeAppName == None:
			print "No app selected!"
			return

		# Next, get the details of the application below this one.
		nextAppName = self.getAppNameByRowNum (self.radioGroup.checkedId() + 1)

		if nextAppName == None:
			print "App is already at lowest position!"
			return

		# We're moveing this one up, so we want to swap with the app
		# above this one.
		activeApp = self.tree.getAppDetails (activeAppName)
		nextApp = self.tree.getAppDetails (nextAppName)
		self.swapSlots (activeApp, nextApp)

		self.buildAppButtons (activeApp ["slot"])

		# Commit changes to disk.
		self.tree.writeTreeToDisk (self.scriptDatabasePath)

	#def editApp (self, appDetails = {}):
		#newApp = NewApplication (appDetails)

		## Wait for the dialog to be closed/canceld/accepted/
		#if not newApp.exec_():
			#return False, appDetails
		
		#returnDetails = newApp.returnNewAppDetails()

		#return True, returnDetails

	def appButtonClicked (self, appName):
		print "button pressed: " + str (appName)

		appDetails = self.tree.getAppDetails (appName)

		if appDetails ["is_group"] == "True":
			self.tree.changeContextToGroup (appName)
			self.buildAppButtons()
			return

	def upLvlBtnClicked (self):
		self.tree.moveContextUpOneLevel()
		self.buildAppButtons()

	def swapSlots (self, appDetails1, appDetails2):

		# Next we'll swap the slot values in the two details we were given.
		slot1 = appDetails1 ["slot"]

		appDetails1 ["slot"] = appDetails2 ["slot"]
		appDetails2 ["slot"] = slot1

		# Finally, commit the apps back into the tree.
		self.tree.updateApp (appDetails1)
		self.tree.updateApp (appDetails2)

class NewApplication (QtGui.QDialog, radioManagement):
	
	def __init__ (self, appDefaultDetails):
		super (NewApplication, self).__init__()

		#self.btnCol = 3
		self.radioCol = 0
		self.gridGridCol = 1
		
		self.gridLabelLabelCol = 0
		self.gridLabelCol = 1
		self.paramReqCol = 2
		#self.defValCol = 1
		#self.reqCol = 2

		radioManagement.__init__ (self, self.radioCol)

		self.initUI()

		self.appDetails = appDefaultDetails.copy()

		self.setValues (appDefaultDetails)

	def initUI (self):
		#self.radioGroup = QtGui.QButtonGroup() # To store radio buttons.

		grid = QtGui.QGridLayout()
		vbox = QtGui.QVBoxLayout()
		#vbox.addStretch (1)

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

		#paramLayout.addWidget (QtGui.QLabel)
		self.initDelAndMovButtons (vbox)

		# Insert "new" button start of edit buttons.
		self.newParamBtn = QtGui.QPushButton ("New &Param", self)
		self.newParamBtn.clicked.connect (self.newParamBtnClicked)
		#self.paramLayout.addWidget (self.newParamBtn, 0, self.btnCol)
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
		#self.cancelBtn.clicked.connect (SLOT ('close()'))
		self.connect (self.cancelBtn, SIGNAL ('clicked()'), SLOT ('reject()'))

		self.okBtn = QtGui.QPushButton ("&ok", self)
		#okBtnWidth = self.cmdBtn.fontMetrics().boundingRect ("ok").width()
		#self.okBtn.setMaximumWidth (okBtnWidth + 15)
		self.okBtn.setDefault(True)
		controlButtonLayout.addWidget (self.okBtn)
		self.okBtn.clicked.connect (self.okBtnClicked)

		self.show()

	def setValues (self, values):
		if "name" in values:
			self.name.setText (values ["name"])
		if "command" in values:
			self.command.setText (values ["command"])
		if "use_sudo" in values:
			pass

		# Set the parameters.
		if "params" in values:
			for param in values ["params"]:
				print "param: " + str(param)
				self.addParameter (param)

		print values

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

		# Horizontal layout for checkboxes.

		# Horizontal layout for text boxes.

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
		showDialog = QtGui.QCheckBox ("file selecter?", self)
		gridLayout.addWidget (showDialog, 1, self.paramReqCol)
		self.setDefaultValue (showDialog, defaultValues, "file_selecter")

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

			## Check that a valid place marker is in "command" edit box.
			#paramCheck = re.search ("(?:[^%]|%%+)%" + \
				#str (index + 1) + "(?:[^0-9]|$)", self.command.text())

			#if paramCheck == None:
			if not self.isParamSymbolPresent (index + 1):
				return False, "Missing parameter symbol '%" + \
					str (index + 1) + "' in command!"

		return True, ""

	def isParamSymbolPresent (self, paramNumber):
		# Check that a valid place marker is in "command" edit box.
		paramCheck = re.search ("(?:[^%]|%%+)%" + \
			str (paramNumber) + "(?:[^0-9]|$)", self.command.text())

		if paramCheck == None:
			return False
		else:
			return True

	def setDefaultValue (self, widget, defaultValues, key):
		if not key in defaultValues:
			print "key not found"
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
			param ["file_selecter"] = widget.isChecked()
			param ["slot"] = rowCount

			params.append (param)

		#print params
		return params

	def returnNewAppDetails (self):
		#newApp = {}
		self.appDetails ["name"] = self.name.text()
		self.appDetails ["command"] = self.command.text()

		if not "use_sudo" in self.appDetails:
			self.appDetails ["use_sudo"] = False
		if not "slot" in self.appDetails:
			self.appDetails ["slot"] = 0

		# We don't use this dialog for creating groups.
		self.appDetails ["is_group"] = "False"

		self.appDetails ["params"] = self.returnParams()

		return self.appDetails

	def newParamBtnClicked (self):
		self.addParameter()

	def deleteButtonClicked (self):
		checkedButtonId = self.radioGroup.checkedId()

		if checkedButtonId == -1:
			print "No item selected!"
			return

		self.deleteRow (self.paramLayout, checkedButtonId)
	
	def moveUpButtonClicked (self):
		# We are moving up, so we'll swap with the row above us.
		
		checkedButtonId = self.radioGroup.checkedId()

		if checkedButtonId == -1:
			print "No item selected!"
			return

		previousButtonRow = checkedButtonId - 1

		if previousButtonRow <= 0:
			print "Row already at highest position!"
			return

		self.swapRows (self.paramLayout, checkedButtonId, previousButtonRow)
	
	def moveDownButtonClicked (self):
		checkedButtonId = self.radioGroup.checkedId()

		if checkedButtonId == -1:
			print "No item selected!"
			return

		nextButtonRow = checkedButtonId + 1

		if nextButtonRow > len (self.radioGroup.buttons()):
			print "Row already at lowest position!"
			return

		self.swapRows (self.paramLayout, checkedButtonId, nextButtonRow)

if __name__ == '__main__':
	# Re-enable "Ctrl+C" terminal interuption.
	signal.signal (signal.SIGINT, signal.SIG_DFL)
	
	app = QtGui.QApplication (sys.argv)
	main = MainWindow()
	main.show()
	sys.exit (app.exec_())
