import unittest
import os.path
import csnBuild
import csnGUIHandler
import warnings

class CSnakeGUIHandlerTest(unittest.TestCase):

	def setUp(self):
		self.handler = csnGUIHandler.Handler()
		thisPath = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")
		self.rootFolder = thisPath
		self.projectFolder1 = thisPath + "/Test1"
		self.projectFolder2 = thisPath + "/Test1/Test2"
		
	def tearDown(self):
		pass
		# os.rmdir(self.projectFolder2)
		
	def testCreateCSnakeFolder(self):
		self.assertRaises(csnGUIHandler.RootNotFound, csnGUIHandler.CreateCSnakeFolder, "d:/notexisting/no123on/test", "d:/notexisting/no123on")
		self.assertRaises(csnGUIHandler.NotARoot, csnGUIHandler.CreateCSnakeFolder, "d:/notexisting/no123on/test", self.rootFolder)

		csnGUIHandler.CreateCSnakeFolder(self.projectFolder2, self.rootFolder)
		assert os.path.exists("%s/__init__.py" % (self.projectFolder1) ), "Not found: %s/__init__.py\n" % (self.projectFolder1)
		assert os.path.exists("%s/__init__.py" % (self.projectFolder2) ), "Not found: %s/__init__.py\n" % (self.projectFolder2)
				
	def testCreateCSnakeProject(self):
		self.assertRaises(csnGUIHandler.TypeError, csnGUIHandler.CreateCSnakeProject, self.projectFolder2, self.rootFolder, "Test2", "lib")
		csnGUIHandler.CreateCSnakeProject(self.projectFolder2, self.rootFolder, "Test2", "library")
		
if __name__ == "__main__":
	unittest.main() 
