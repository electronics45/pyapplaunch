#import appdirs
import ConfigParser
import os.path

def getPyapplaunchConfigDir ():
	#pyapplaunchConfigDir = appdirs.user_data_dir ("pyapplaunch")

	pyapplaunchDir = os.path.dirname (os.path.abspath (__file__))
	pyapplaunchConfigDir = os.path.join (pyapplaunchDir, "config")

	# If the directory does not exist, then create it.
	if not os.path.exists (pyapplaunchConfigDir):
		os.makedirs (pyapplaunchConfigDir)

	return pyapplaunchConfigDir

def getPyapplaunchImageDir ():
	pyapplaunchDir = os.path.dirname (os.path.abspath (__file__))
	pyapplaunchImageDir = os.path.join (pyapplaunchDir, "images")

	return pyapplaunchImageDir

class ConfigManager ():
	def __init__ (self):
		self.configFileName = "pyapplaunch.config"

		# Store an instance of the config parser which will hold
		# options from our config file.
		self.configParser = ConfigParser.ConfigParser()

		self.readConfigFile()

	def readConfigFile (self):
		configFilePath = os.path.join (getPyapplaunchConfigDir(), self.configFileName)
		self.configParser.read (configFilePath)

	def writeConfigFile (self):
		configFilePath = os.path.join (getPyapplaunchConfigDir(), self.configFileName)

		with open (configFilePath, "w") as fileHandle:
			self.configParser.write (fileHandle)

	def getConfigSection (self, sectionName):
		sectionDict = {}

		if not self.configParser.has_section (sectionName):
			# Section by this name has no entry, so we'll just
			# return an empty dictionary for completeness.
			return {}

		options = self.configParser.options (sectionName)

		for option in options:
			try:
				sectionDict [option] = self.configParser.get (sectionName, option)
				if sectionDict [option] == -1:
					pass

			except:
				print ("exception on %s!" % option)
				sectionDict [option] = None

		return sectionDict

	def setSection (self, sectionName, values):
		# If this section already exists, remove it, so we can start fresh.
		if self.configParser.has_section (sectionName):
			self.configParser.remove_section (sectionName)

		self.configParser.add_section (sectionName)

		for key, value in values.iteritems():
			self.configParser.set (sectionName, key, value)

	def getItemInSection (self, sectionName, key):
		if not self.configParser.has_section (sectionName):
			return None

		return self.configParser.get (sectionName, key)

	def getItemInSectionInt (self, sectionName, key):
		if not self.configParser.has_section (sectionName):
			return None

		return self.configParser.getint (sectionName, key)

	def setItemInSection (self, sectionName, key, value):
		if not self.configParser.has_section (sectionName):
			self.configParser.add_section (sectionName)

		self.configParser.set (sectionName, key, value)
