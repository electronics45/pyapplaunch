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
		#except:
			#raise

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
		#appNode = xml.Element (str (appDetails ["name"]))
		appNode = xml.Element ("application")
		self.currentContext.append (appNode)

		nameNode = xml.Element ("name")
		nameNode.text = str (appDetails ["name"])
		appNode.append (nameNode)

		self.updateApp (appDetails)

	def getNodeByName (self, name, parentNode = None):
		# Get a list of all application nodes.
		#appNodes = self.currentContext.findall ("./application")
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
		#appNode = self.currentContext.find (appDetails ["name"])
		appNode = self.getNodeByName (appDetails ["name"])

		if appNode == None:
			raise RuntimeError ("Could not find app '" + appName + "' in current context '" + str (self.currentContext.tag) + "'.")

		# Iterate over all properties to be updated.
		for key in appDetails.keys():
			## Note that the "name" node has already been used in the node's tag.
			## Note that "name tag" 
			#if key == "name":
				#continue

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

		#app = self.currentContext.find (appName)
		app = self.getNodeByName (appName)

		if app == None:
			raise RuntimeError ("Could not find app '" + appName + "' in current context '" + str (self.currentContext.tag) + "'.")

		# Start with the applications name (stored as tag).
		#dictionary ["name"] = app.tag

		# Build a dictionary of all the apps child elements.
		for appProperty in app:
			if appProperty.tag == "params":
				dictionary [appProperty.tag] = self.getAppParams (appProperty)
			else:
				dictionary [appProperty.tag] = appProperty.text

		return dictionary

	def renameAndUpdateApp (self, originalName, newDetails):
		# First, we'll update the name.
		#app = self.currentContext.find (originalName)
		app = self.getNodeByName (originalName)

		if app == None:
			raise RuntimeError ("Could not find app '" + originalName + "' in current context '" + str (self.currentContext.tag) + "'.")

		#app.tag = newDetails ["name"]
		app.find ("name").text = newDetails ["name"]

		# Next, update the details.
		self.updateApp (newDetails)

	def deleteApp (self, name):
		# If an app with this name exists, modify it instead of creating a new one.
		#appNode = self.currentContext.find (name)
		appNode = self.getNodeByName (name)

		if appNode == None:
			raise RuntimeError ("Could not find app '" + name + "' in current context '" + str (self.currentContext.tag) + "'.")

		self.currentContext.remove (appNode)

	def getApplications (self):
		applications = []

		# Build a list of dictionaries from the tree's nodes of the app's.
		for app in self.currentContext:
			## Push this dictionary into the applications list.
			#applications.append (self.getAppDetails (app.tag))
			applications.append (self.getAppDetails (app.find ("name").text))
			#details = self.getAppDetails (self.getNodeByName ("name", app).text)
			#applications.append (details)

		#print applications

		self.sortListBySlot (self.currentContext, applications)

		return applications

	def sortListBySlot (self, parentNode, theList):
		theList = sorted (theList, key = lambda app: app ["slot"])

		# Finally, we'll reset the "slot" number in case an app was deleted, etc.
		for i, app in enumerate (theList):
			app ["slot"] = str (i + 1) # "slot" is indexed from "1", not "0".

			#parentNode.find (app ["name"]).find ("slot").text = str (i + 1)
			self.getNodeByName (app ["name"], parentNode).find ("slot").text = str (i + 1)
	def getNumApps (self):
		# Is there not a nicer way to do this?
		return len (list (self.currentContext))

	def doesAppExistInCurrentContext (self, appName):
		#if self.currentContext.find (appName):
		if self.getNodeByName (appName):
			return True
		else:
			return False

	def getNode (self, parent, key):
		#node = parent.find (key)
		node = self.getNodeByName (key, parent)
		if node == None:
			# Child node does not yet exist, so lets create it.
			node = xml.Element (str (key))
			#node = xml.Element ("application")
			parent.append (node)

			#nameNode = xml.Element ("name")
			#nameNote.text = keys
			#parentNode.

		return node

	def setAppParams (self, paramsNode, params):

		# Start by removing all the old params.
		for node in paramsNode:
			paramsNode.remove (param)

		for param in params:
			#paramNode = self.getNode (paramsNode, param ["name"])
			#paramNode = self.getNodeByName (param ["name"], paramsNode)

			paramNode = xml.Element ("param")
			paramsNode.append (paramNode)
			#nameNode = xml.Element (param ["name"])
			#nameNode.text = xml.Element (param ["name"])
			#paramNode.append (nameNode)

			# Iterate over all properties to be updated.
			for key in param.keys():
				# Note that the "name" node has already been used in the node's tag.
				#if key == "name":
					#continue

				childNode = self.getNode (paramNode, key)

				childNode.text = str (param [key])
	
	def getAppParams (self, paramsNode):
		params = []

		for paramNode in paramsNode:
			param = {}

			#param ["name"] = paramNode.tag

			# Gather all the properties of the paramater.
			for paramChild in paramNode:
				param [paramChild.tag] = paramChild.text

				# We don't want any "None"'s, so replace with empty string.
				if param [paramChild.tag] == None:
					param [paramChild.tag] = ""

			params.append (param)

		# Sort the parameters.
		#self.sortListBySlot (paramsNode)
		
		return params

	def changeContextToGroup (self, groupName):
		self.contextTrail.append (self.currentContext)

		#self.currentContext = self.currentContext.find (groupName).find("children")
		self.currentContext = self.getNodeByName (groupName).find("children")

	def isRootContext (self):
		if self.currentContext == self.root:
			return True
		else:
			return False

	def moveContextUpOneLevel (self):
		#self.currentContext = self.currentContext.findall ("..")
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
