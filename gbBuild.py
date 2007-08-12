from os import makedirs
import os.path

def Join(theList):
	"""
	Returns a string that contains the items of theList separated by spaces.
	"""
	all = ""
	for x in theList:
		all = all + str(x) + " "
	return all

class Generator:
	"""
	Generates the CMakeLists.txt for a gbBuild.Project.
	"""

	def Generate(self, _project, _binaryFolder):
		"""
		Generates the CMakeLists.txt for a gbBuild.Project in _binaryFolder.
		"""
		
		# create binary project folder
		binaryProjectFolder = "%s/modules/%s" % (_binaryFolder, _project.name)
		os.path.exists(binaryProjectFolder) or os.makedirs(binaryProjectFolder)
		
		# open cmakelists.txt
		fileCMakeLists = "%s/CMakeLists.txt" % (binaryProjectFolder)
		f = open(fileCMakeLists, 'w')
		
		# write header and some cmake fields
		f.write( "# CMakeLists.txt generated automatically by GBuild.py.\n" )
		f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
		f.write( "PROJECT(%s)\n" % (_project.name) )
		f.write( "INCLUDE_DIRECTORIES(%s)\n" % (Join(_project.publicIncludePaths)) )
	
		# find and use dependent projects
		f.write( "\n# Include dependency projects\n\n" )
		for dependencyProject in _project.dependencyProjects:
			f.write( "FIND_PACKAGE(%s)\n" % (dependencyProject.name) )			
			f.write( "INCLUDE(${%s_USE_FILE})\n" % (dependencyProject.name) )

		# write section that is specific for the project type		
		f.write( "\n# Add target\n\n" )
		if(_project.type == "executable" ):
			f.write( "ADD_EXECUTABLE(%s %s)\n" % (_project.name, Join(_project.sources)) )
			
		elif(_project.type == "library" ):
			f.write( "ADD_LIBRARY(%s %s)\n" % (_project.name, Join(_project.sources)) )
		
		elif(_project.type == "dll" ):
			f.write( "ADD_LIBRARY(%s %s)\n" % (_project.name, Join(_project.sources)) )
			
		else:
			raise NameError, "Unknown project type %s" % _project.type

		f.close()
		pass
		
class Project:
	"""
	Contains the data for the makefile (or vcproj) for a project.
	_name -- Name of the project, e.g. \"SampleApp\"
	_type -- Type of the project, should be \"executable\", \"library\" or \"dll\"
	"""
	
	def Init(self, _name, _type):
		self.publicIncludePaths = []
		self.publicLibraryPaths = []
		self.sources = []
		self.name = _name
		self.type = _type
		self.dependencyProjects = []
		
	def AddDependency(self, otherProject):
		self.dependencyProjects.append( otherProject )
		self.dependencyProjects.extend( otherProject.dependencyProjects )
		