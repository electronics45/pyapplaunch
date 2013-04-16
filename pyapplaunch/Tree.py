import xml.etree.cElementTree as xml
import json

class Tree ():
	def __init__ (self, treePath):
		self.rootName = "applications"

		self.root = None
		self.currentContext = None

		self.contextTrail = []

		try:
			self.readTreeFromDisk (treePath)
		except:
			print "could not read tree '" + treePath + "'; building default."
			pass
		
		if self.root == None:
			self.buildDefaultTree()

	def buildDefaultTree (self):
		self.root = xml.Element (self.rootName)
		self.currentContext = self.root

	def writeTreeToDisk (self, writeTarget):
		targetfile = open (writeTarget, 'w')

		self.indent (self.root)

		try:  # Using a try block ensures file is always closed.
			xml.ElementTree (self.root).write (targetfile)
		finally:
			targetfile.close()
	
	def readTreeFromDisk (self, readTarget):
		tree = xml.parse (readTarget)
		
		self.root = tree.getroot()
		self.currentContext = self.root

	def addApp (self, appDetails):
		# Create a child element, and append it to the root node.
		appNode = xml.Element ("application")
		self.currentContext.append (appNode)

		# Append the "name" node first which is needed to identify this node.
		nameNode = xml.Element ("name")
		nameNode.text = str (appDetails ["name"])
		appNode.append (nameNode)

		self.updateApp (appDetails)

	def getNodeByName (self, name, parentNode = None):
		if parentNode == None:
			parentNode = self.currentContext

		# Find the child node that has the "name" subnode with a value of "name".
		for node in parentNode:
			nameNode = node.find ("name")
			if nameNode != None and nameNode.text == name:
				return node

		# Failed to find node.
		return None

	def updateApp (self, appDetails):
		appNode = self.getNodeByName (appDetails ["name"])

		if appNode == None:
			appName = appDetails ["name"]
			raise RuntimeError ("Could not find app '" + appName + "' in current context '" + str (self.currentContext.tag) + "'.")

		# Iterate over all properties to be updated.
		for key in appDetails.keys():
			childNode = self.getNode (appNode, key)

			if key == "params":
				# We won't keep this node around if there are not params.
				if len (appDetails [key]) == 0:
					appNode.remove (childNode)

				# We'll Now write a new "param" node for each of the parameters.
				# for param in appDetails [key]:
				self.setAppParams (childNode, appDetails [key])

				continue

			childNode.text = str (appDetails [key])

	def getAppDetails (self, appName):
		dictionary = {}

		app = self.getNodeByName (appName)

		if app == None:
			raise RuntimeError ("Could not find app '" + appName + "' in current context '" + str (self.currentContext.tag) + "'.")

		# Build a dictionary of all the apps child elements.
		for appProperty in app:
			if appProperty.tag == "params":
				dictionary [appProperty.tag] = self.getAppParams (appProperty)
			else:
				dictionary [appProperty.tag] = appProperty.text

		return dictionary

	def renameAndUpdateApp (self, originalName, newDetails):
		# First, we'll update the name.
		app = self.getNodeByName (originalName)

		if app == None:
			raise RuntimeError ("Could not find app '" + originalName + "' in current context '" + str (self.currentContext.tag) + "'.")

		app.find ("name").text = newDetails ["name"]

		# Next, update the details.
		self.updateApp (newDetails)

	def deleteApp (self, name):
		appNode = self.getNodeByName (name)

		if appNode == None:
			raise RuntimeError ("Could not find app '" + name + "' in current context '" + str (self.currentContext.tag) + "'.")

		self.currentContext.remove (appNode)

	def getApplications (self):
		applications = []

		# Build a list of dictionaries from the tree's nodes of the app's.
		for app in self.currentContext:
			# Push this dictionary into the applications list.
			applications.append (self.getAppDetails (app.find ("name").text))

		applications = self.sortListBySlot (self.currentContext, applications)

		return applications

	def sortListBySlot (self, parentNode, theList):
		theList = sorted (theList, key = lambda app: app ["slot"])

		# Finally, we'll reset the "slot" number in case an app was deleted, etc.
		for i, app in enumerate (theList):
			app ["slot"] = str (i + 1) # "slot" is indexed from "1", not "0".

			slotNode = self.getNodeByName (app ["name"], parentNode).find ("slot")
			slotNode.text = str (i + 1)
		return theList

	def getNumApps (self):
		# TODO: Is there not a nicer way to do this?
		return len (list (self.currentContext))

	def doesAppExistInCurrentContext (self, appName):
		if self.getNodeByName (appName):
			return True
		else:
			return False

	def getNode (self, parent, key):
		node = parent.find (key)

		if node == None:
			# Child node does not yet exist, so lets create it.
			node = xml.Element (str (key))
			parent.append (node)

		return node

	def setAppParams (self, paramsNode, params):

		# Start by removing all the old params.
		for node in paramsNode:
			paramsNode.remove (param)

		# Rebuild the param tree.
		for param in params:
			paramNode = xml.Element ("param")
			paramsNode.append (paramNode)

			# Iterate over all properties to be updated.
			for key in param.keys():
				childNode = self.getNode (paramNode, key)

				childNode.text = str (param [key])

	def getAppParams (self, paramsNode):
		params = []

		for paramNode in paramsNode:
			param = {}

			# Gather all the properties of the paramater.
			for paramChild in paramNode:
				param [paramChild.tag] = paramChild.text

				# We don't want any "None"'s, so replace with empty string.
				if param [paramChild.tag] == None:
					param [paramChild.tag] = ""

			params.append (param)

		return params

	def substituteEveryOccurrenceOfValue (self, oldValue, newValue, key, startNode = None):
		if startNode == None:
			startNode = self.root

		# Iterate over the child nodes.
		for node in startNode:
			keyNode = node.find (key)

			# If we find the key as a child, and it's value matches the old value.
			if keyNode != None and keyNode.text == oldValue:
				keyNode.text = str (newValue)

			childrenNode = node.find ("children")
			if childrenNode != None:
				# This is also a group node, so we'll process it's children.
				self.substituteEveryOccurrenceOfValue (oldValue, newValue,
					key, childrenNode)

	def changeContextToGroup (self, groupName):
		self.contextTrail.append (self.currentContext)

		self.currentContext = self.getNodeByName (groupName).find("children")

	def isRootContext (self):
		if self.currentContext == self.root:
			return True
		else:
			return False
			
	def returnToRootContext (self):
		self.currentContext = self.root

	def moveContextUpOneLevel (self):
		self.currentContext = self.contextTrail.pop()

	def indent (self, elem, level = 0):
		i = "\n" + level*"  "
		if len (elem):
			if not elem.text or not elem.text.strip():
				elem.text = i + "  "
			if not elem.tail or not elem.tail.strip():
				elem.tail = i
			for elem in elem:
				self.indent (elem, level + 1)
			if not elem.tail or not elem.tail.strip():
				elem.tail = i
		else:
			if level and (not elem.tail or not elem.tail.strip()):
				elem.tail = i
