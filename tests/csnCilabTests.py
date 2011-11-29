## @package csnCilabTests
# Definition of the csnCilabTests class.
# \ingroup tests
import unittest
import csnProject
import csnCilab
import csnBuild
import csnContext
import shutil

class csnCilabTests(unittest.TestCase):
    """ Unit tests for for the csnCilab methods. """
    
    def setUp(self):
        """ Run before test. """
        # load fake context
        self.context = csnContext.Load("config/csnake_context.txt")
        # change the build folder
        self.context.SetBuildFolder(self.context.GetBuildFolder() + "/build")
        # set it as global context
        csnProject.globalCurrentContext = self.context

    def tearDown(self):
        """ Run after test. """
        csnProject.globalCurrentContext = None

    def testCreateHeader(self):
        """ testCreateHeader: test the CreateHeader method. """
        project = csnProject.Project("Project", "library")
        project.AddCustomCommand( csnCilab.CreateToolkitHeader )
        
        # generate
        generator = csnBuild.Generator()
        generator.Generate(project)

        # check that the headerFile is there
        path = "%s/%s" % (project.GetBuildFolder(), "CISTIBToolkit.h")
        headerFile = open(path, 'r')
        foundSrcPath = False
        foundBuildPath = False
        for line in headerFile:
            if not foundSrcPath:
                if line.find("CISTIB_TOOLKIT_FOLDER") != -1:
                    foundSrcPath = True 
            if not foundBuildPath:
                if line.find("CISTIB_TOOLKIT_BUILD_FOLDER") != -1:
                    foundBuildPath = True
        headerFile.close()
        # test
        self.assertTrue(foundSrcPath)
        self.assertTrue(foundBuildPath)
        
        # clean up
        shutil.rmtree( csnProject.globalCurrentContext.GetBuildFolder() )
        
if __name__ == "__main__":
    unittest.main() 
