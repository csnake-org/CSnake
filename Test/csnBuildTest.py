import unittest
import os.path
import csnBuild
import warnings

class GlobalTestSetup:

	def setUp(self):
		"""
		Create projects and (on disk) some source files.
		"""

		# define bin folder
		thisPath = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")
		self.binFolder = "%s/%s" % (thisPath, "temp_bin")
		
		# find cmake and devenv
		if( os.environ.has_key('CSNAKE_TEST_CMAKE_EXE') ):
			self.cmakePath = os.environ['CSNAKE_TEST_CMAKE_EXE']
		else:
			self.cmakePath = "cmake"
			warnings.warn( "$(CSNAKE_TEST_CMAKE_EXE) exe file not defined, cmake.exe needs to be in the search path.\n" )
			
		if( os.environ.has_key('CSNAKE_TEST_DEVENV_COM') ):
			self.devenvPath = os.environ['CSNAKE_TEST_DEVENV_COM']
		else:
			self.devenvPath = "devenv"
			warnings.warn( "$(CSNAKE_TEST_DEVENV_COM) com file not defined, devenv.com needs to be in the search path.\n" )
		
	def stearDown(self):
		pass

class ProjectTest(unittest.TestCase):

	def setUp(self):
		"""
		Create projects and (on disk) some source files.
		"""
		self.globalTestSetup = GlobalTestSetup()
		self.globalTestSetup.setUp()

		self.dummyDll = csnBuild.Project("DummyDll", "dll")
		self.dummyDll.AddPublicIncludeFolders(["DummyDll"])
		self.dummyDll.AddSources(["DummyDll/DummyDll.cpp", "DummyDll/DummyDll.h"])
		self.dummyDll.AddDefinitions(["DummyDllDefPrivateWin32"], _private = 1, _WIN32 = 1)

		self.dummyLib = csnBuild.Project("DummyLib", "library")
		self.dummyLib.AddPublicIncludeFolders(["DummyLib"])
		self.dummyLib.AddSources(["DummyLib/DummyLib.cpp", "DummyLib/DummyLib.h"])
		self.dummyLib.AddProject(self.dummyDll)
		self.dummyLib.AddDlls(["DummyLib/lib/ExtraLib.dll"])
		self.dummyDll.AddDefinitions(["DummyLibDefPublicWin32"], _private = 0, _WIN32 = 1)
		
		self.dummyExe = csnBuild.Project("DummyExe", "executable")
		self.dummyExe.AddPublicIncludeFolders(["DummyExe"])
		self.dummyExe.AddSources(["DummyExe/DummyExe.cpp"])
		self.dummyExe.AddProject(self.dummyLib)
		self.dummyExe.AddDefinitions(["DummyExeDefPrivate"], _private = 1)
		
	def stearDown(self):
		self.globalTestSetup.tearDown()
		
	def testHasBackSlash(self):
		""" Test HasBackSlash function. """
		assert csnBuild.HasBackSlash("c:\\hallo")
		assert not csnBuild.HasBackSlash("c://hallo")
		
	def testGenerate(self):
		""" Test configuring the dummy project. """
		
		# generate cmake files
		generator = csnBuild.Generator()
		generator.Generate(self.dummyExe, self.globalTestSetup.binFolder)
		
	def testBuild(self):
		""" Test configuring and building the dummy project. """
		
		# generate cmake files
		generator = csnBuild.Generator()
		generator.Generate(self.dummyExe, self.globalTestSetup.binFolder)
		
		# run cmake to generate solution
		cmdString = "%s %s/%s >cmake.log" % (self.globalTestSetup.cmakePath, self.globalTestSetup.binFolder, self.dummyExe.cmakeListsSubpath)
		ret = os.system(cmdString)
		assert ret == 0, "CMake returned with an error message."
		
		# run devenv to build solution
		solutionFile = "%s/%s/%s.sln" % (self.globalTestSetup.binFolder, self.dummyExe.binarySubfolder, self.dummyExe.name)
		assert os.path.exists(solutionFile)
		cmdString = "%s /build Debug %s >devenv.log" % (self.globalTestSetup.devenvPath, solutionFile)
		ret = os.system(cmdString)
		assert ret == 0, "devenv returned with an error message."

		# test the built executable
		exeFilename = "%s/bin/debug/%s.exe" % (self.globalTestSetup.binFolder, self.dummyExe.name)
		assert os.path.exists(exeFilename)
		ret = os.system(exeFilename)
		assert ret == 6, "DummyExe.exe did not return the correct calculation result."
		
	def testInit(self):
		self.assertEqual(self.dummyLib.name, "DummyLib")

	def testSourceRootFolder(self):
		""" Test that the source root folder, containing csnBuildTest.py, is deduced correctly by the parent class csnBuild.Project. """
		self.assertEqual(os.path.abspath(self.dummyLib.sourceRootFolder), os.path.abspath(os.path.dirname(__file__)))
	
	def testSelfDependency(self):
		""" Test that a project cannot depend on itself. """
		self.assertRaises(csnBuild.DependencyError, self.dummyExe.AddProject, self.dummyExe)
		
	def testAddProjectTwice(self):
		""" Test that adding a project twice has no effect. """
		i = len(self.dummyExe.childProjects)
		self.dummyExe.AddProject(self.dummyLib)
		self.assertEqual(i, len(self.dummyExe.childProjects))

	def testCyclicDependency(self):
		""" Test that a cylic dependency is detected. """
		self.assertRaises( csnBuild.DependencyError, self.dummyDll.AddProject, self.dummyExe)

	def testNonExistingSourceFile(self):
		""" Test that a non-existing source file is detected. """
		self.assertRaises(IOError, self.dummyDll.AddSources, ["main.cpp"])
		
	def testNonExistingIncludeFolder(self):
		""" Test that a non-existing include folder is detected. """
		self.assertRaises(IOError, self.dummyDll.AddPublicIncludeFolders, ["include"])
	
	def testBuildBinFolderSlashes(self):
		""" Test that build bin folder may not contain any backward slashes. """
		generator = csnBuild.Generator()
		thisPath = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")
		binFolder = "%s\\%s" % (thisPath, "temp_bin")
		self.assertRaises(csnBuild.SyntaxError, generator.Generate, self.dummyExe, binFolder)

	def testGlob(self):
		""" Test that globbing source files works. """
		p = csnBuild.Project("DummyDll", "dll")
		p.AddSources(["Dummy*/*.h"])
		assert len(p.sources) == 2, csnBuild.Join(p.sources)
		
	def testNameConflict(self):
		""" Test that two projects cannot have the same name. """
		dummyLib = csnBuild.Project("DummyLib", "library")
		dummyLib.AddPublicIncludeFolders(["DummyLib"])
		dummyLib.AddSources(["DummyLib/DummyLib.cpp", "DummyLib/DummyLib.h"])
		self.dummyExe.AddProject(dummyLib)
		generator = csnBuild.Generator()
		self.assertRaises(NameError, generator.Generate, self.dummyExe, self.globalTestSetup.binFolder)
		
if __name__ == "__main__":
	unittest.main() 
