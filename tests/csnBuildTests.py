## @package csnBuildTests
# Definition of the csnBuildTests class.
# \ingroup tests
import unittest
import csnBuild
import csnProject
import shutil
import csnContext

class csnBuildTests(unittest.TestCase):
    """ Generic build tests. """

    def setUp(self):
        """ Run before test. """

    def tearDown(self):
        """ Run after test. """

    def testGenerate(self):
        """ csnBuildTest: test configuring a dummy project. """
        # load fake context
        self.context = csnContext.Load("config/csnake_context.txt")
        # change the build folder
        self.context.SetBuildFolder(self.context.GetBuildFolder() + "/build")
        # set it as global context
        csnProject.globalCurrentContext = self.context

        # dummyExe project
        dummyExe = csnProject.Project("DummyExe", "executable")
        
        # generate cmake files
        generator = csnBuild.Generator()
        generator.Generate(dummyExe)
        # clean up
        shutil.rmtree( csnProject.globalCurrentContext.GetBuildFolder() )
        
if __name__ == "__main__":
    unittest.main() 
