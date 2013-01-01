import xml.etree.cElementTree as xml

class Tree ():
	def __init__ (self, treePath):
		self.rootName = "applications"
		
		self.root = None
		self.currentContext = None

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
		appNode = xml.Element (str (appDetails ["name"]))
		self.root.append (appNode)

		# Now append the remaing properties as additional nested nodes.
		node = xml.Element ("command")
		node.text = str (appDetails ["command"])
		appNode.append (node)

		# Other properties.
		if "use_sudo" in appDetails:
			node = xml.Element ("use_sudo")
			node.text = str (appDetails ["use_sudo"])
			appNode.append (node)
		if "slot" in appDetails:
			node = xml.Element ("slot")
			node.text = str (appDetails ["slot"])
			appNode.append (node)

	def updateApp (self, appDetails):
		appNode = self.currentContext.find (appDetails ["name"])

		if appNode == None:
			raise RuntimeError ("Could not find app '" + appName + "' in current context '" + str (self.currentContext.tag) + "'.")

		# Iterate over all properties to be updated.
		for key in appDetails.keys():
			childNode = appNode.find (key)
			if childNode == None:
				# Child node does not yet exist, so lets create it.
				childNode = xml.Element (key)
				appNode.append (childNode)

			childNode.text = appDetails [key]

	def getAppDetails (self, appName):
		dictionary = {}

		app = self.currentContext.find (appName)

		if app == None:
			raise RuntimeError ("Could not find app '" + appName + "' in current context '" + str (self.currentContext.tag) + "'.")

		# Start with the applications name (stored as tag).
		dictionary ["name"] = app.tag

		# Build a dictionary of all the apps child elements.
		for appProperty in app:
			dictionary [appProperty.tag] = appProperty.text

		return dictionary


	def deleteApp (self, name):
		# If an app with this name exists, modify it instead of creating a new one.
		appNode = self.currentContext.find (name)

		if appNode == None:
			raise RuntimeError ("Could not find app '" + name + "' in current context '" + str (self.currentContext.tag) + "'.")

		self.currentContext.remove (appNode)

	def getApplications (self):
		applications = []

		# Build a list of dictionaries from the tree's nodes of the app's.
		for app in self.currentContext:
			## Push this dictionary into the applications list.
			applications.append (self.getAppDetails (app.tag))

		# Now we'll order the applications based on their "slot" number.
		# "lambda" just creates an unnamed function with "app" as a parameter.
		applications = sorted (applications, key = lambda app: app ["slot"])

		# Finally, we'll reset the "slot" number in case an app was deleted, etc.
		#for i in range (len (applications)):
			#applications [i]["slot"] = i
		for i, app in enumerate (applications):
			app ["slot"] = str (i + 1) # "slot" is indexed from "1", not "0".

			self.currentContext.find (app ["name"]).find ("slot").text = str (i + 1)

		# Finally, we must commit these slot numbers back to the tree to avoid disparity.
		#for app in self.currentContext:
			#app.find ("slot").text = applications
		#for appDetails in applications	
		#print applications

		return applications

	def getNumApps (self):
		# Is there not a nicer way to do this?
		return len (list (self.currentContext))

	def doesAppExist (self, appName):
		if self.root.find (appName):
			return True
		else:
			return False

	def setAppParam (self, appName, paramNumber, required = False, defaultValue = None):
		pass
	
	def deleteAppParam (self, appName, paramNumber):
		pass
	
	def getAppParams (self, appName):
		pass

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
