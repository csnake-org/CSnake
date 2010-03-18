# Unit tests for for the csnBuild class
import unittest
import os.path
import csnBuild
import csnProject
import csnGUIHandler
import shutil
import subprocess
import ConfigParser

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
        
    def testDummyExeBuild(self):
        """ testDummyExeBuild: test configuring and building the DummyExe project. """
        self.build( "DummyExe", "executable", "Release" )
        
    def testDummyLibBuild(self):
        """ testDummyLibBuild: test configuring and building the DummyLib project. """
        self.build( "DummyLib", "lib", "Release" )

    def build(self, projectName, type, buildMode):
        """ test configuring and building the input project. """
        # names
        instanceName = projectName.lower()[0] + projectName[1:]
        contextFileName = "config/csnake_context.txt"
        contextNewFileName = "config/csnake_context-%s.txt" % projectName
        sectionName = "CSnake"
        if type == "executable":
            exeName = projectName
        # ok, a bit fishy, I know the application name...
        elif type == "lib":
            exeName = projectName + "App_myApp"
        
        # modify the csnake context file
        cf = ConfigParser.ConfigParser()
        cf.read(contextFileName)
        # modify the options
        cf.set(sectionName, "instance", instanceName)
        csnakefile = cf.get(sectionName, "csnakefile")
        csnakefile = csnakefile.replace("TestInstance", projectName)
        cf.set(sectionName, "csnakefile", csnakefile)
        # save the new context file
        contextNewFile = open(contextNewFileName, 'w')
        cf.write(contextNewFile)
        contextNewFile.close()
        
        # create GUI handler
        handler = csnGUIHandler.Handler()
        # load context
        context = handler.LoadContext(contextNewFileName)
        
        # configure the project
        ret = handler.ConfigureProjectToBuildFolder( True )        
        # check that it worked
        assert ret == True, "CMake returned with an error message."
        
        # create compiler command
        mainMode = "Release"
        if( context.compilername.find("Visual Studio") != -1 ):
            # check solution file
            solutionFile = handler.GetTargetSolutionPath()
            assert os.path.exists(solutionFile)
            mode = mainMode
            path = "\"%s\"" % context.idePath
            # Incredibuild case
            if( context.idePath.find("BuildConsole") != -1 ):
                mode = "\"%s|x64\"" % mainMode
                path = "%s" % context.idePath
            cmdString = "%s %s /build %s" % (path, solutionFile, mode )
        elif( context.compilername.find("KDevelop3") != -1 or
              context.compilername.find("Makefile") != -1 ):
            cmdString = "cd ../bin/executable/%s/%s; make -s" % (mainMode, projectName) 
        
        # run compiler    
        ret = subprocess.call(cmdString, shell=True)
        assert ret == 0, "The compiler returned with an error message."

        # check the built executable
        exeFilename = "%s/bin/%s/%s" % (context.buildFolder, mainMode, exeName)
        if( context.compilername.find("Visual Studio") != -1 ):
            exeFilename = "%s.exe" % (exeFilename)
        assert os.path.exists(exeFilename)
        
        # test the built executable
        ret = subprocess.call(exeFilename, shell=True)
        assert ret == 6, "The generated executable did not return the correct result."

        # clean up
        shutil.rmtree( csnProject.globalCurrentContext.buildFolder )
        
if __name__ == "__main__":
    unittest.main() 
