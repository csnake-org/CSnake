# Unit tests for for the csnBuild class
import unittest
import os.path
import csnBuild
import csnProject
import csnGUIHandler
import shutil

class csnBuildTests(unittest.TestCase):

    def setUp(self):
        """ Run before test. """

    def tearDown(self):
        """ Run after test. """

    def testGenerate(self):
        """ csnBuildTest: test configuring a dummy project. """
        # dummyExe project
        dummyExe = csnProject.Project("DummyExe", "executable")
        
        # generate cmake files
        generator = csnBuild.Generator()
        generator.Generate(dummyExe)
        # clean up
        shutil.rmtree( csnProject.globalCurrentContext.buildFolder )
        
    def testBuild(self):
        """ csnBuildTest: test configuring and building the dummy project. """
        
        # create GUI handler
        handler = csnGUIHandler.Handler()
        # load context
        context = handler.LoadContext("config/csnake_context.txt")
        
        # configure the project
        ret = handler.ConfigureProjectToBuildFolder( True )        
        # check that it worked
        assert ret == True, "CMake returned with an error message."
        
        # check solution file
        solutionFile = handler.GetTargetSolutionPath()
        assert os.path.exists(solutionFile)
        
        # run devenv to build solution
        logFile = "devenv.log"
        cmdString = "\"%s\" /build Debug %s > %s" % (context.idePath, solutionFile, logFile)
        print cmdString
        ret = os.system(cmdString)
        assert ret == 0, "devenv returned with an error message."

        # check the built executable
        exeName =  handler.GetListOfPossibleTargets()[0]
        exeFilename = "%s/bin/debug/%s.exe" % (context.buildFolder, exeName)
        assert os.path.exists(exeFilename)
        
        # test the built executable
        ret = os.system(exeFilename)
        assert ret == 6, "DummyExe.exe did not return the correct calculation result."

        # clean up
        shutil.rmtree( csnProject.globalCurrentContext.buildFolder )
        os.remove(logFile)
        
if __name__ == "__main__":
    unittest.main() 
