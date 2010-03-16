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
        print context.compilername
        if( context.compilername.find("Visual Studio") != -1 ):
            mode = "Release"
            # Incredibuild case
            if( context.idePath.find("BuildConsole") != -1 ):
                mode = "Release|x64" 
            cmdString = "\"%s\" %s /build %s" % (context.idePath, solutionFile, mode )
        elif( context.compilername.find("KDevelop3") != -1 or
              context.compilername.find("Makefile") != -1 ):
            cmdString = "./bin/executable/DummyExe/make -s"
            
        print cmdString
        ret = os.system(cmdString)
        assert ret == 0, "Compiler returned with an error message."

        # check the built executable
        exeName =  handler.GetListOfPossibleTargets()[0]
        exeFilename = "%s/bin/%s/%s" % (context.buildFolder, mode, exeName)
        if( context.compilername.find("Visual Studio") != -1 ):
            exeFilename = "%s.exe" % (exeFilename)
        assert os.path.exists(exeFilename)
        
        # test the built executable
        print exeFilename
        ret = os.system(exeFilename)
        assert ret == 6, "DummyExe did not return the correct result."

        # clean up
        shutil.rmtree( csnProject.globalCurrentContext.buildFolder )
        
if __name__ == "__main__":
    unittest.main() 
