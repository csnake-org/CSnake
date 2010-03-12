# Unit tests for for the csnGUIHandler class
import unittest
import os.path
import csnGUIHandler
import csnCreate
import shutil

class csnGUIHandlerTests(unittest.TestCase):

    def setUp(self):
        """ Run before test. """
        self.handler = csnGUIHandler.Handler()
        thisPath = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")
        self.rootFolder = thisPath
        self.projectFolder1 = thisPath + "/Test1"
        self.projectFolder2 = thisPath + "/Test1/Test2"
        
    def tearDown(self):
        """ Run after test. """
        # clean up folders
        shutil.rmtree(self.projectFolder1)
        
    def testCreateCSnakeFolder(self):
        """ csnGUIHandlerTest: test create csnake folder."""
        # test exception when projectRoot (second argument) does not exist
        self.assertRaises(csnGUIHandler.RootNotFound, csnCreate.CreateCSnakeFolder, "d:/notexisting/no123on/test", "d:/notexisting/no123on")
        # test exception when folder (first arg) is not in projectRoot (second argument)
        self.assertRaises(csnGUIHandler.NotARoot, csnCreate.CreateCSnakeFolder, "d:/notexisting/no123on/test", self.rootFolder)

        # create the folders
        csnCreate.CreateCSnakeFolder(self.projectFolder2, self.rootFolder)
        # check that first level exists
        assert os.path.exists("%s/__init__.py" % (self.projectFolder1) ), "Not found: %s/__init__.py\n" % (self.projectFolder1)
        # check that second level exists
        assert os.path.exists("%s/__init__.py" % (self.projectFolder2) ), "Not found: %s/__init__.py\n" % (self.projectFolder2)
                
    def testCreateCSnakeProject(self):
        """ csnGUIHandlerTest: test create csnake project."""
        # test that type (fourth argument) 'lib' is not accepted
        self.assertRaises(TypeError, csnCreate.CreateCSnakeProject, self.projectFolder2, self.rootFolder, "Test2", "lib")
        # create the project
        csnCreate.CreateCSnakeProject(self.projectFolder2, self.rootFolder, "Test2", "library")
        
if __name__ == "__main__":
    unittest.main() 
