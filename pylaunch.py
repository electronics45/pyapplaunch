#! /usr/bin/python

from PyQt4.QtCore import *
from PyQt4 import QtGui
import signal
import sys
import os

#import xml.etree.cElementTree as xml

from radioManagement import radioManagement
from Tree import Tree

#class radioManagement ():
	#def __init__ (self, radioCol):
		#self.radioGroup = QtGui.QButtonGroup() # To store radio buttons.
		#self.radioCol = radioCol

	#def initDelAndMovButtons (self, vLayout):
		### A horizontal rule.
		##line = QtGui.QFrame (self)
		##line.setFrameShape (QtGui.QFrame.HLine)
		##line.setFrameShadow (QtGui.QFrame.Sunken)
		##vLayout.addWidget (line)

		## Add hbox for edit buttons.
		#self.editHBox = QtGui.QHBoxLayout()
		#self.editHBox.addStretch (1)
		#vLayout.addLayout (self.editHBox)

		#button = QtGui.QPushButton ("&Delete", self)
		#self.editHBox.addWidget (button)
		#self.connect (button, SIGNAL ("clicked()"), self.deleteButtonClicked)

		#button = QtGui.QPushButton ("Move &Up", self)
		#self.editHBox.addWidget (button)
		#self.connect (button, SIGNAL ("clicked()"), self.moveUpButtonClicked)

		#button = QtGui.QPushButton ("Move Do&wn", self)
		#self.editHBox.addWidget (button)
		#self.connect (button, SIGNAL ("clicked()"), self.moveDownButtonClicked)

	#def buildRow (self, gridLayout, row = 0):
		##row = gridLayout.rowCount() + 1

		## Create the radio button for editing of the app.
		#radio = QtGui.QRadioButton (str (row), self)
		#gridLayout.addWidget (radio, row, self.radioCol)
		#self.radioGroup.addButton(radio, row)

	#def setCheckedRadioButtonByRow (self, row):
		#print "row: " + str (row)
		#for radio in self.radioGroup.buttons():
			#if radio.text() == str (row):
				#radio.setChecked (True)
				#return

		## Radio button not found.
		#raise RuntimeError ("Could not find radio at row: " + str (row))

	#def clearGridLayout (self, gridLayout):
		## This function removes all of the automatically generated
		## buttons and such from the layout.

		## Remove the radio buttons fromt "radioGroup".
		#for buttonEntry in self.radioGroup.buttons():
			#self.radioGroup.removeButton (buttonEntry)

		#for i in range (gridLayout.rowCount()):
			#for j in range (gridLayout.columnCount()):
				#widgetItem = gridLayout.itemAtPosition (i, j)
				
				#if widgetItem != None:
					#widgetItem.widget().setParent (None)

	#def getWidgetAtCheckedRow (self, gridLayout, column):
		#checkedButtonId = self.radioGroup.checkedId()

		#if checkedButtonId == -1:
			## No radio buttons are checked.
			#return None

		## widged at "checkedButtonId"'s row.
		#return gridLayout.itemAtPosition (checkedButtonId, column).widget()

	#def deleteRow (self, gridLayout, rowNum):
		## What we'll actually do, is leave the radio buttons in tact, but 
		## delete all the other widgets in the row.  Then we'll move everything
		## else up, and finally delete the last radio button.

		#for i in range (gridLayout.columnCount()):
			## Skip the radio button's column.
			#if i == self.radioCol:
				#continue

			#widgetItem = gridLayout.itemAtPosition (rowNum, i)

			#if widgetItem == None:
				#continue

			## Delete the widget.
			#widgetItem.widget().setParent (None)

		## Next, move everything up row by row.  +1 is to offset from the row we just deleted.
		#for i in range (rowNum + 1, gridLayout.rowCount()):
			#for j in range (gridLayout.columnCount()):
				#if j == self.radioCol:
					#continue

				#widgetItem = gridLayout.itemAtPosition (i, j)

				#if widgetItem == None:
					#continue

				#gridLayout.addWidget (widgetItem.widget(), i - 1, j)

		## Finally, delete the last row.
		#for i in range (gridLayout.columnCount()):
			#widgetItem = gridLayout.itemAtPosition (gridLayout.rowCount() - 1, i)

			#if widgetItem == None:
				#continue

			## Delete the widget.
			#widgetItem.widget().setParent (None)

	#def swapRows (self, gridLayout, row1, row2):
		#row1Widgets = {}

		#for i in range (gridLayout.columnCount()):
			#widgetItem = gridLayout.itemAtPosition (row1, i)

			#if widgetItem == None:
				#continue

			#widget1 = widgetItem.widget()
			#widget2 = gridLayout.itemAtPosition (row2, i).widget()

			## Is this the radio button widget?
			#if i == self.radioCol:
				## We don't want to move the radio buttons, but
				## we do want change which is checked, if applicable.
				#if widget1.isChecked():
					#widget2.setChecked (True)
				#elif widget2.isChecked():
					#widget1.setChecked (True)

				#continue

			#gridLayout.addWidget (widget2, row1, i)
			#gridLayout.addWidget (widget1, row2, i)


	#def deleteButtonClicked (self):
		#pass
	
	#def moveUpButtonClicked (self):
		#pass
	
	#def moveDownButtonClicked (self):
		#pass

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

		self.mainWidget.setLayout (vbox)
		self.setWindowTitle ("PyLaunch")

	def buildAppButtons (self, defaultSlot = None):
		row = 1

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

			row += 1

		#if defaultSlot != None:
			#self.setCheckedRadioButtonBySlot (defaultSlot)

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

		originalName = details ["name"]

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
			return False, appDetails
		
		returnDetails = newApp.returnNewAppDetails()

		return returnDetails, True

	def editGroupName (self, defaultDetails):
		details = defaultDetails.copy()

		details ["name"], ok = QtGui.QInputDialog.getText (self, 'New Group',
			'Enter a name for the new group:', QtGui.QLineEdit.Normal,
			details ["name"])

		return details, ok

	def showNewApp (self):
		#wasAccepted, appDetails = self.editApp ({})

		## Has the user cancelled?
		#if not wasAccepted:
			#return

		## Check for name clashes.
		## Keep Retrying until the user succeeds.
		#while self.tree.doesAppExistInCurrentContext (appDetails ["name"]) == True:
			#error = QtGui.QErrorMessage(self)
			#error.showMessage ("Script with that name already exists!")
			#error.exec_()

			#if not wasAccepted:
				#return  # User changed their mind.

			#wasAccepted, appDetails = self.editApp (appDetails)

		## Set the slot to 1 past the number of app registered here.
		#appDetails ["slot"] = self.tree.getNumApps() + 1

		##print self.tree.getNumApps()

		## Add this new app to the tree.
		#self.tree.addApp (appDetails)

		## Rebuild the buttons.
		#self.buildAppButtons()

		## Save new configuration to disk.
		#self.tree.writeTreeToDisk (self.scriptDatabasePath)

		self.createNewButton (self.editAppDetails)

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
		#["slot"]

		#print appDetails
		#print newAppDetails

		## Easiest thing to do now is delete the old app, and add a
		## new one.
		#self.tree.deleteApp (appDetails ["name"])
		#self.tree.addApp (newAppDetails)

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
		elif len (self.command.text()) == 0:
			error.showMessage ("No command selected!")
			error.exec_()
		elif self.areAllParamsValid() == False:
			error.showMessage ("Parameter is missing a name!")
			error.exec_()
		else:
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

	def areAllParamsValid (self):
		# The only required value for a paramter is a label (name).
		for param in self.returnParams():
			if param ["name"] == "":
				print "No name for param #" + str (param ["slot"])
				return False

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

#class Application ():
	#def __init__ (self):
		#pass
	
	#def launch (self):
		#pass
	
	#def AddParam (
		#isPassword = False,
		#useSudo = False,
		#defaultValue = "",
		#required = False,
		#prependParam = "",
		#appendParam = ""
		#):
		#pass
		
#class Tree ():
	#def __init__ (self, treePath):
		#self.rootName = "applications"
		
		#self.root = None
		#self.currentContext = None

		#try:
			#self.readTreeFromDisk (treePath)
		#except:
			#print "could not read tree '" + treePath + "'; building default."
			#pass
		##except:
			##raise

		#if self.root == None:
			#self.buildDefaultTree()

	#def buildDefaultTree (self):
		#self.root = xml.Element (self.rootName)
		#self.currentContext = self.root

	#def writeTreeToDisk (self, writeTarget):
		#targetfile = open (writeTarget, 'w')

		#self.indent (self.root)

		#try:  # Using a try block ensures file is always closed.
			#xml.ElementTree (self.root).write (targetfile)
		#finally:
			#targetfile.close()
	
	#def readTreeFromDisk (self, readTarget):
		#tree = xml.parse (readTarget)
		
		#self.root = tree.getroot()
		#self.currentContext = self.root

	#def addApp (self, appDetails):
		## Create a child element, and append it to the root node.
		#appNode = xml.Element (str (appDetails ["name"]))
		#self.root.append (appNode)

		## Now append the remaing properties as additional nested nodes.
		#node = xml.Element ("command")
		#node.text = str (appDetails ["command"])
		#appNode.append (node)

		## Other properties.
		#if "use_sudo" in appDetails:
			#node = xml.Element ("use_sudo")
			#node.text = str (appDetails ["use_sudo"])
			#appNode.append (node)
		#if "slot" in appDetails:
			#node = xml.Element ("slot")
			#node.text = str (appDetails ["slot"])
			#appNode.append (node)

	#def updateApp (self, appDetails):
		#appNode = self.currentContext.find (appDetails ["name"])

		#if appNode == None:
			#raise RuntimeError ("Could not find app '" + appName + "' in current context '" + str (self.currentContext.tag) + "'.")

		## Iterate over all properties to be updated.
		#for key in appDetails.keys():
			#childNode = appNode.find (key)
			#if childNode == None:
				## Child node does not yet exist, so lets create it.
				#childNode = xml.Element (key)
				#appNode.append (childNode)

			#childNode.text = appDetails [key]

	#def getAppDetails (self, appName):
		#dictionary = {}

		#app = self.currentContext.find (appName)

		#if app == None:
			#raise RuntimeError ("Could not find app '" + appName + "' in current context '" + str (self.currentContext.tag) + "'.")

		## Start with the applications name (stored as tag).
		#dictionary ["name"] = app.tag

		## Build a dictionary of all the apps child elements.
		#for appProperty in app:
			#dictionary [appProperty.tag] = appProperty.text

		#return dictionary


	#def deleteApp (self, name):
		## If an app with this name exists, modify it instead of creating a new one.
		#appNode = self.currentContext.find (name)

		#if appNode == None:
			#raise RuntimeError ("Could not find app '" + name + "' in current context '" + str (self.currentContext.tag) + "'.")

		#self.currentContext.remove (appNode)

	#def getApplications (self):
		#applications = []

		## Build a list of dictionaries from the tree's nodes of the app's.
		#for app in self.currentContext:
			### Push this dictionary into the applications list.
			#applications.append (self.getAppDetails (app.tag))

		## Now we'll order the applications based on their "slot" number.
		## "lambda" just creates an unnamed function with "app" as a parameter.
		#applications = sorted (applications, key = lambda app: app ["slot"])

		## Finally, we'll reset the "slot" number in case an app was deleted, etc.
		##for i in range (len (applications)):
			##applications [i]["slot"] = i
		#for i, app in enumerate (applications):
			#app ["slot"] = str (i + 1) # "slot" is indexed from "1", not "0".

			#self.currentContext.find (app ["name"]).find ("slot").text = str (i + 1)

		## Finally, we must commit these slot numbers back to the tree to avoid disparity.
		##for app in self.currentContext:
			##app.find ("slot").text = applications
		##for appDetails in applications	
		##print applications

		#return applications

	#def getNumApps (self):
		## Is there not a nicer way to do this?
		#return len (list (self.currentContext))

	#def doesAppExist (self, appName):
		#if self.root.find (appName):
			#return True
		#else:
			#return False

	#def setAppParam (self, appName, paramNumber, required = False, defaultValue = None):
		#pass
	
	#def deleteAppParam (self, appName, paramNumber):
		#pass
	
	#def getAppParams (self, appName):
		#pass

	#def indent (self, elem, level = 0):
		#i = "\n" + level*"  "
		#if len (elem):
			#if not elem.text or not elem.text.strip():
				#elem.text = i + "  "
			#if not elem.tail or not elem.tail.strip():
				#elem.tail = i
			#for elem in elem:
				#self.indent (elem, level + 1)
			#if not elem.tail or not elem.tail.strip():
				#elem.tail = i
		#else:
			#if level and (not elem.tail or not elem.tail.strip()):
				#elem.tail = i

#class AppParam ():
	#def __init__ (self):
		#self.isPassword = False
		#self.useSudo = False
		#self.defaultValue = ""
		#self.required = False
		#self.prependParam = ""
		#self.appendParam = ""

if __name__ == '__main__':
	# Re-enable "Ctrl+C" terminal interuption.
	signal.signal (signal.SIGINT, signal.SIG_DFL)
	
	app = QtGui.QApplication (sys.argv)
	main = MainWindow()
	main.show()
	sys.exit (app.exec_())