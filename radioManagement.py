from PyQt4.QtCore import *
from PyQt4 import QtGui

class radioManagement ():
	def __init__ (self, radioCol, gridLayout):
		self.radioGroup = QtGui.QButtonGroup() # To store radio buttons.
		self.radioCol = radioCol
		self.gridLayout = gridLayout

	def initDelAndMovButtons (self, vLayout):

		# Add hbox for edit buttons.
		self.editHBox = QtGui.QHBoxLayout()
		self.editHBox.addStretch (1)
		vLayout.addLayout (self.editHBox)

		button = QtGui.QPushButton ("&Delete", self)
		self.editHBox.addWidget (button)
		self.connect (button, SIGNAL ("clicked()"), self.deleteButtonClicked)

		button = QtGui.QPushButton ("Move &Up", self)
		self.editHBox.addWidget (button)
		self.connect (button, SIGNAL ("clicked()"), self.moveUpButtonClicked)

		button = QtGui.QPushButton ("Move Do&wn", self)
		self.editHBox.addWidget (button)
		self.connect (button, SIGNAL ("clicked()"), self.moveDownButtonClicked)

	def buildRow (self, gridLayout, row = 0):
		# Create the radio button for editing of the app.
		radio = QtGui.QRadioButton (str (row), self)
		gridLayout.addWidget (radio, row, self.radioCol)
		self.radioGroup.addButton(radio, row)

	def setCheckedRadioButtonByRow (self, row):
		for radio in self.radioGroup.buttons():
			if radio.text() == str (row):
				radio.setChecked (True)
				return

		# Radio button not found.
		raise RuntimeError ("Could not find radio at row: " + str (row))

	def clearGridLayout (self):
		# This function removes all of the automatically generated
		# buttons and such from the layout.

		# Remove the radio buttons fromt "radioGroup".
		for buttonEntry in self.radioGroup.buttons():
			self.radioGroup.removeButton (buttonEntry)

		for i in range (self.gridLayout.rowCount()):
			for j in range (self.gridLayout.columnCount()):
				widgetItem = self.gridLayout.itemAtPosition (i, j)
				
				if widgetItem != None:
					widgetItem.widget().setParent (None)

	def getWidgetAtCheckedRow (self, column):
		checkedButtonId = self.radioGroup.checkedId()

		if checkedButtonId == -1:
			# No radio buttons are checked.
			return None

		# widged at "checkedButtonId"'s row.
		return self.gridLayout.itemAtPosition (checkedButtonId, column).widget()

	def deleteRow (self, rowNum):
		rowCount = self.getRowCount()
		
		# What we'll actually do, is leave the radio buttons in tact, but 
		# delete all the other widgets in the row.  Then we'll move everything
		# else up, and finally delete the last radio button.

		for i in range (self.gridLayout.columnCount()):
			# Skip the radio button's column.
			if i == self.radioCol:
				continue

			widgetItem = self.gridLayout.itemAtPosition (rowNum, i)

			# Delete the widget.
			self.deleteWidgetItem (widgetItem)

		# Next, move everything up row by row.  +1 is to offset from the row we just deleted.
		for i in range (rowNum + 1, rowCount + 1):
			for j in range (self.gridLayout.columnCount()):
				if j == self.radioCol:
					continue

				widgetItem = self.gridLayout.itemAtPosition (i, j)

				#if widgetItem == None:
					#continue

				#gridLayout.addWidget (widgetItem.widget(), i - 1, j)
				self.addWidgetItem (self.gridLayout, widgetItem, i - 1, j)

		# We'll also need to remove the radio button's reference from "radioGroup".
		lastRadioButon = self.gridLayout.itemAtPosition (rowCount, self.radioCol)
		self.radioGroup.removeButton (lastRadioButon.widget())

		# Finally, delete the last row.
		for i in range (self.gridLayout.columnCount()):
			widgetItem = self.gridLayout.itemAtPosition (rowCount, i)

			# Delete the widget.
			self.deleteWidgetItem (widgetItem)
		
		self.gridLayout.invalidate()

	def swapRows (self, row1, row2):
		row1Widgets = {}

		for i in range (self.gridLayout.columnCount()):
			widgetItem1 = self.gridLayout.itemAtPosition (row1, i)
			widgetItem2 = self.gridLayout.itemAtPosition (row2, i)

			if widgetItem1 == None:
				continue

			a = widgetItem1.widget()
			b = widgetItem2.widget()

			# Is this the radio button widget?
			if i == self.radioCol:
				# We don't want to move the radio buttons, but
				# we do want change which is checked, if applicable.
				if widgetItem1.widget().isChecked():
					widgetItem2.widget().setChecked (True)
				elif widgetItem2.widget().isChecked():
					widgetItem1.widget().setChecked (True)

				continue

			self.addWidgetItem (widgetItem2, row1, i)
			self.addWidgetItem (widgetItem1, row2, i)

	def deleteWidgetItem (self, widgetItem):
		# If the item is actually empty.
		if widgetItem == None:
			return

		# Check if it is a widget (and not a layout).
		widget = widgetItem.widget()
		if widget != None:
			# Delete the widget item.
			widgetItem.widget().setParent (None)
			return

		# No? then it must be a layout.
		layout = widgetItem.layout()

		if type (layout) != QtGui.QGridLayout:
			for i in range (len (layout)):
				self.deleteWidgetItem (layout.itemAt (i))
		else:
			# We'll just be assuming a grid layout here, since there
			# isn't any convinient method to do otherwise.
			for i in range (layout.rowCount()):
				for j in range (layout.columnCount()):

					self.deleteWidgetItem (layout.itemAtPosition (i, j))

		# Finally, delete the empty layout.
		layout.setParent (None)

	def addWidgetItem (self, widgetItem, posX, posY):
		if widgetItem == None:
			return

		widget = widgetItem.widget()

		if widget != None:
			# Looks like we're processing a widget.
			self.gridLayout.addWidget (widget, posX, posY)
			return

		# We otherwise assume it's a layout.
		layout = widgetItem.layout()

		# Bug in PyQt.  Causes segfault if I do not do this.
		# I guess I /could/ go and fix it in the source...
		layout.setParent (None)

		self.gridLayout.addLayout (layout, posX, posY)

	def getRowCount (self):
		# Unfortunately, gridLayout.rowCount() is unreliable for getting the number
		# rows in the grid, so we need an alternative method.
		return len (self.radioGroup.buttons())

	def getRowRange (self):
		# Return the range of values from 1 (first param) to the number of rows,
		# include the final value (achieved by +1 offset).
		return range (1, len (self.radioGroup.buttons()) + 1)

	def deleteButtonClicked (self):
		pass
	
	def moveUpButtonClicked (self):
		pass
	
	def moveDownButtonClicked (self):
		pass

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

		self.swapRows (checkedButtonId, previousButtonRow)

	def moveDownButtonClicked (self):
		checkedButtonId = self.radioGroup.checkedId()

		if checkedButtonId == -1:
			print "No item selected!"
			return

		nextButtonRow = checkedButtonId + 1

		if nextButtonRow > len (self.radioGroup.buttons()):
			print "Row already at lowest position!"
			return

		self.swapRows (checkedButtonId, nextButtonRow)
