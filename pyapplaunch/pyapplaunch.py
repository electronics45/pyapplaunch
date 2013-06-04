#! /usr/bin/python

from PyQt4.QtCore import *
from PyQt4 import QtGui
import signal
import sys
import os
from functools import partial

from ApplicationLauncher import ApplicationLauncher
from ConfigManager import ConfigManager
from DbusInterface import DbusInterface
from ExecutionDelegate import *
from NewApplication import *
from RadioManagement import RadioManagement
from Tree import Tree

class MainWindow (QtGui.QMainWindow, RadioManagement):
	def __init__ (self):
		QtGui.QMainWindow.__init__ (self)

		self.btnCol = 1
		self.radioCol = 0

		self.upDirShortCutKey = "/"
		self.homeDirShortCutKey = "-"

		self.pyapplaunchConfigDir = ConfigManager.getPyapplaunchConfigDir()

		self.configManager = ConfigManager.ConfigManager()
		self.executionManager = ExecutionDelegateManager (self.configManager)

		self.scriptDatabasePath = self.pyapplaunchConfigDir + os.sep + "scripts.xml"

		self.tree = Tree (self.scriptDatabasePath)
		
		self.upButton = None
		self.homeButton = None

		self.initUI()
		self.buildAppButtons()
		self.createSysTray()
		self.restoreWindowPos()

		# This is an adaptor to call "self.tree.substituteEveryOccurrenceOfValue"
		# with the right parameters, since the signal we're connecting to can't
		# connect directly to the function.
		nameChangeAdaptor = lambda s1, s2: \
			self.tree.substituteEveryOccurrenceOfValue (s1, s2, "exec_with")
		self.executionManager.delegateNameChanged.connect (nameChangeAdaptor)

	def closeEvent (self, event):
		self.hideWindow()
		event.ignore()

	def quit (self):
		self.saveWindowPos()
		QtGui.qApp.quit()

	def saveWindowPos (self):
		# Save position of window.
		pos = self.pos()
		self.configManager.setItemInSection ("window_settings", "pos_x", str (pos.x()))
		self.configManager.setItemInSection ("window_settings", "pos_y", str (pos.y()))
		self.configManager.writeConfigFile()

	def restoreWindowPos (self):
		posX = self.configManager.getItemInSectionInt ("window_settings", "pos_x")
		posY = self.configManager.getItemInSectionInt ("window_settings", "pos_y")

		if posX == None or posY == None:
			# Failed to get one of the settings, so we won't move the window.
			return

		self.move (posX, posY)

	def showWindow (self):
		self.show()
		self.restoreWindowPos()

	def hideWindow (self):
		self.hide()
		self.saveWindowPos()

	def toggleWindow (self):
		if self.isHidden() == False:
			self.hideWindow()
		else:
			self.showWindow()

	def createSysTray (self):
		self.sysTray = QtGui.QSystemTrayIcon (self)
		self.sysTray.setIcon (self.windowIcon())
		self.sysTray.setVisible (True)
		self.connect (self.sysTray, SIGNAL ("activated (QSystemTrayIcon::ActivationReason)"), self.onSysTrayActivated)

		menu = QtGui.QMenu (self)
		exitAction = menu.addAction (self.exitAction)

		self.sysTray.setContextMenu (menu)

	def onSysTrayActivated (self, reason):
		if reason == 3:
			self.toggleWindow()
	
	def returnToHomeContext (self):
		self.tree.returnToRootContext()
		self.buildAppButtons()
		self.updateTiteContextPath()
		
	def contextUpLevel (self):
		self.tree.moveContextUpOneLevel()
		self.buildAppButtons()
		self.updateTiteContextPath()
	
	def updateTiteContextPath (self):
		path = self.tree.getContextPath()

		# Put the current context path into the title-bar for convinience.
		self.setWindowTitle ("PyLaunch - " + path)

	def initUI (self):
		# Set the icon for the window.
		imageDir = ConfigManager.getPyapplaunchImageDir()
		self.setWindowIcon (QtGui.QIcon (os.path.join (imageDir, "pyapplaunch.png")))

		QtGui.QShortcut (QtGui.QKeySequence ("Esc"), self, self.hide)
		QtGui.QShortcut (QtGui.QKeySequence ("Ctrl+Q"), self, self.quit)

		# Exit action for menus.
		self.exitAction = QtGui.QAction(QtGui.QIcon ('exit.png'), '&Exit', self)
		self.exitAction.setShortcut ('Ctrl+Q')
		self.exitAction.setStatusTip ('Exit application')
		self.exitAction.triggered.connect (self.quit)
		
		# Add a "home" shortcut key to return to the root context.
		QtGui.QShortcut (QtGui.QKeySequence ("-"), self, self.returnToHomeContext)
		
		# Add a "home" shortcut key to return to the root context.
		QtGui.QShortcut (QtGui.QKeySequence ("/"), self, self.contextUpLevel)

		#menubar = self.menuBar()
		#fileMenu = menubar.addMenu ('&File')
		#fileMenu.addAction (self.exitAction)

		self.mainWidget = QtGui.QWidget (self) # dummy to contain the layout.
		self.setCentralWidget (self.mainWidget)

		vbox = QtGui.QVBoxLayout()
		vbox.addStretch (1)

		# This layout will hold the script buttons once they're generated.
		self.buttonLayout = QtGui.QGridLayout()
		vbox.addLayout (self.buttonLayout)
		self.buttonLayout.setColumnStretch (self.btnCol, 1) # Btn column stretches most.

		RadioManagement.__init__ (self, self.radioCol, self.buttonLayout)

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
		self.setWindowTitle ("PyLaunch - /")

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
				self.setCheckedRadioButtonByRow (row)

			# Create the button.
			button = QtGui.QPushButton (app ["name"], self)
			self.buttonLayout.addWidget (button, row, self.btnCol)

			# Bind that button to a method which calls another method,
			# passing the name of the button being clicked to it.
			closure = partial (self.appButtonClicked, app ["name"])
			self.connect (button, SIGNAL ("clicked()"), closure)

			# Add a correspinding number as a shortcut key, provided we
			# Do not go past "9"
			if row <= 9:
				button.setShortcut (QtGui.QKeySequence (str(row)))
			elif row == 10:
				# Set the "0" number as the short cut for item 10.
				button.setShortcut (QtGui.QKeySequence (str(0)))

			# We want a different colour for groups so we can tell themself.homeDirShortCutKey
			# appart.
			if app ["is_group"] == "True":
				self.setGroupButtonColour (button)

			row += 1

		# Build return navigation buttons
		if not self.tree.isRootContext():
			hbox = QtGui.QHBoxLayout()
			self.buttonLayout.addLayout (hbox, row, self.btnCol)

			# Build a button to take us up one level if we're not in the root context.
			self.upButton = QtGui.QPushButton ("Go Up One Level", self)
			hbox.addWidget (self.upButton)
			self.connect (self.upButton, SIGNAL ("clicked()"), self.contextUpLevel)
			self.setGroupButtonColour (self.upButton)

			# Build the button to return to home context.
			self.homeButton = QtGui.QPushButton ("Home", self)
			hbox.addWidget (self.homeButton)
			self.connect (self.homeButton, SIGNAL ("clicked()"), self.returnToHomeContext)
			self.setGroupButtonColour (self.homeButton)

	def clearAppButtons (self):
		self.clearGridLayout()
		
		if self.upButton != None:
			self.upButton.setParent (None)
		if self.homeButton != None:
			self.homeButton.setParent (None)

	def getActiveAppName (self):
		button = self.getWidgetAtCheckedRow (self.btnCol)

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
		while self.tree.doesAppExistInCurrentContext (details ["name"]) == True or \
			details ["name"][0].isdigit():
			if details ["name"] == originalName:
				# Looks like the user decided to keep the original name.
				break

			error = QtGui.QErrorMessage (self)
			if details ["name"][0].isdigit():
				error.showMessage ("Script name can not start with a number!")
			else:
				error.showMessage ("Script with that name already exists!")
				
			error.exec_()

			details, ok = editMethod (details)

			if not ok:
				return details, False  # User changed their mind.

		return details, True

	def editAppDetails (self, defaultDetails):
		newApp = NewApplication (defaultDetails, self.executionManager)

		self.connect (self, SIGNAL ("closing()"), newApp.close)

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

		# Normalise values to strings.
		details ["name"] = str (details ["name"])

		return details, ok

	def showNewApp (self):
		self.createNewButton (self.editAppDetails)

	def setGroupButtonColour (self, button):
		button.setStyleSheet("QPushButton {color:black; background-color: grey;}")

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

			if not wasAccepted:
				return

			# Easiest thing to do now is delete the old app, and add a new one.
			self.tree.deleteApp (appDetails ["name"])
			self.tree.addApp (newAppDetails)

		else:
			originalName = appDetails ["name"]

			newAppDetails, wasAccepted = self.editDetails (self.editGroupName,
				appDetails)

			if not wasAccepted:
				return

			print newAppDetails
			print originalName
			self.tree.renameAndUpdateApp (originalName, newAppDetails)

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

		self.deleteRow (self.radioGroup.checkedId())

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

		self.swapSlots (activeApp, nextApp)

		self.swapRows (checkedRow, swapRow)

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

	def appButtonClicked (self, appName):
		appDetails = self.tree.getAppDetails (appName)

		if appDetails ["is_group"] == "True":
			self.tree.changeContextToGroup (appName)
			self.buildAppButtons()
			self.updateTiteContextPath()
			return

		launchProgram = self.executionManager.getDelegates() [appDetails ["exec_with"]]

		launcher = ApplicationLauncher (appDetails, launchProgram)
		launcher.waitForParamsAndExecute()

	#def upLvlBtnClicked (self):
		#self.tree.moveContextUpOneLevel()
		#self.buildAppButtons()

	def swapSlots (self, appDetails1, appDetails2):

		# Next we'll swap the slot values in the two details we were given.
		slot1 = appDetails1 ["slot"]

		appDetails1 ["slot"] = appDetails2 ["slot"]
		appDetails2 ["slot"] = slot1

		# Finally, commit the apps back into the tree.
		self.tree.updateApp (appDetails1)
		self.tree.updateApp (appDetails2)

def main():
	# Re-enable "Ctrl+C" terminal interuption.
	signal.signal (signal.SIGINT, signal.SIG_DFL)

	app = QtGui.QApplication (sys.argv)

	main = MainWindow()
	main.show()
	
	dbusInterface = DbusInterface (main)
	
	sys.exit (app.exec_())

if __name__ == '__main__':
	main()
