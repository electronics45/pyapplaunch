import re
import shlex
import subprocess
from functools import partial

from PyQt4.QtCore import *
from PyQt4 import QtGui

class ApplicationLauncher ():
	def __init__ (self, applicationDetails, launchProg):
		self.appDetails = applicationDetails
		self.launchProg = launchProg
		self.cmdString = self.appDetails ["command"]

	def waitForParamsAndExecute (self):
		# Only initialise the gui if there are parameters to be collected.  If
		# Not, we can skip this, and go strait to executing the program.
		if "params" in self.appDetails and len (self.appDetails ["params"]) != 0:
			dialog = ExecDialog (self.appDetails)
			if not dialog.exec_():
				return False

			self.params = dialog.getParameters()
		else:
			self.params = []

		self.formatCommandString ()

		self.execute()

	def execute (self):
		# Build the full cmd sequence as a list, spliting each parameter at
		# the spaces, but preserving anything inside quotes as a single parameter.
		cmd = shlex.split (self.launchProg) + shlex.split (self.cmdString)

		#print "executing: " + str (cmd)

		try:
			proc = subprocess.Popen(cmd)
		except OSError, e:
			error = QtGui.QErrorMessage ()
			error.showMessage ("Error calling execution program: " + e.strerror)
			error.exec_()
			return

	def formatCommandString (self):
		index = 0
		tokenCount = 0
		outString = ""
		inStrLen = len (self.cmdString)

		# Iterate over every character to find substitution characters.
		#for index, char in enumerate (self.cmdString):
		while index < inStrLen:
			currentParam = None

			# We only care about about characters
			if self.cmdString [index] != "%":
				outString += self.cmdString [index]
			elif index >= inStrLen:
				# A trailing %?  Oh well, lets presume it's supose to be
				# a literal %.
				outString.append (char)
				
			# Is the next character another "%"?
			elif self.cmdString [index + 1] == "%":
				# Substitue with a literal "%"
				outString.append ("%")
				index += 1 # Extra increment.
				
			elif not self.cmdString [index + 1].isdigit():
				# A "%" without a numeral, or another "%" following.
				# Presume user just wanted a literal "%"
				outString.append ("%")

			else: # Only the option of a parameter token remains.
				# Found a parameter token; Get all digets.
				token = re.search ("^[0-9]+", self.cmdString[index + 1:]).group(0)

				# Append this parameter to it's proper place.
				# - 1 is to offset for the 1-based indexing of the tokens.
				outString += self.params [int (token) - 1]

				#tokenCount += 1
				index += len (token)

			index += 1

		self.cmdString = outString

class ExecDialog (QtGui.QDialog):
	def __init__ (self, appDetails):
		super (ExecDialog, self).__init__()

		self.appDetails = appDetails

		self.initUI()

	def initUI (self):
		vbox = QtGui.QVBoxLayout()
		self.paramGrid = QtGui.QGridLayout()

		self.parameters = []

		# Text boxes stretch the most.
		self.paramGrid.setColumnStretch (1, 1)

		# Grid layout to hold parameters.
		vbox.addLayout (self.paramGrid)

		# Set window properties
		self.setGeometry (300, 300, 290, 150)
		self.setWindowTitle ("Add New Script")
		self.setLayout (vbox)

		self.populateParameters()

		controlButtonLayout = QtGui.QHBoxLayout()
		vbox.addLayout (controlButtonLayout)

		# Execute and cancel buttons.
		button = QtGui.QPushButton ("&cancel", self)
		controlButtonLayout.addWidget (button)
		self.connect (button, SIGNAL ('clicked()'), SLOT ('reject()'))

		button = QtGui.QPushButton ("&execute", self)
		button.setDefault(True)
		controlButtonLayout.addWidget (button)
		button.clicked.connect (self.execBtnClicked)

		# Let there be GUI!
		self.show()

	def populateParameters (self):
		for row, param in enumerate (self.appDetails ["params"]):
			label = QtGui.QLabel (param ["name"] + ":", self)
			self.paramGrid.addWidget (label, row, 0)

			editBox = QtGui.QLineEdit (self)
			self.paramGrid.addWidget (editBox, row, 1)

			# Set the default value.
			editBox.setText (param ["default"])

			# Insert the "choose file" dialog button, if appropriate.
			if param ["file_selector"] == "True":
				btn = QtGui.QPushButton ("...", self)
				self.paramGrid.addWidget (btn, row, 2)
				btnWith = btn.fontMetrics().boundingRect ("...").width()
				btn.setMaximumWidth (btnWith + 15)
				closure = partial (self.selectFileClicked, row)
				btn.clicked.connect (closure)

	def getParameters (self):
		return self.parameters

	def storeParameters (self):
		self.parameters = []

		for row in range (self.paramGrid.rowCount()):
			item = self.paramGrid.itemAtPosition (row, 1)

			if item == None:
				continue

			self.parameters.append (str (item.widget().text()))

	def areParamsOk (self):
		for i, param in enumerate (self.appDetails ["params"]):
			if len (self.parameters [i]) == 0 and \
				param ["required"] == "True":

				error = QtGui.QErrorMessage (self)
				error.showMessage ("Required parameter '" + \
					param ["name"] + "' has not been entered!")
				error.exec_()

				return False

		return True

	def execBtnClicked (self):
		# Check that all "required" parameters are filled in.
		self.storeParameters()

		if self.areParamsOk():
			self.accept()

	def selectFileClicked (self, row):
		text = QtGui.QFileDialog.getOpenFileName (self, 'Select File')

		if len (text) != 0:
			self.paramGrid.itemAtPosition (row, 1).widget().setText (text)
