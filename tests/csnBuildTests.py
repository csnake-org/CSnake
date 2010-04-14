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

    def build(self, projectName, buildType, buildMode):
        """ test configuring and building the input project. """
        # names
        instanceName = projectName.lower()[0] + projectName[1:]
        contextFileName = "config/csnake_context.txt"
        contextNewFileName = "config/csnake_context-%s.txt" % projectName
        csnakeSectionName = "CSnake"
        
        # modify the csnake context file
        cf = ConfigParser.ConfigParser()
        cf.read(contextFileName)
        # modify the options
        cf.set(csnakeSectionName, "instance", instanceName)
        csnakefile = cf.get(csnakeSectionName, "csnakefile")
        csnakefile = csnakefile.replace("TestInstance", projectName)
        cf.set(csnakeSectionName, "csnakefile", csnakefile)
        # no spaces for cmake/make
        if( cf.get(csnakeSectionName, "compilername").find("KDevelop3") != -1 or
              cf.get(csnakeSectionName, "compilername").find("Makefile") != -1 ):
            options = ["csnakefile", "thirdpartyrootfolder"]
            for option in options:
                tmp = cf.get(csnakeSectionName, option)
                tmp = tmp.replace("my src", "src")
                cf.set(csnakeSectionName, option, tmp)
            options = ["buildfolder", "thirdpartybuildfolder"]
            for option in options:
                tmp = cf.get(csnakeSectionName, option)
                tmp = tmp.replace("my bin", "bin")
                cf.set(csnakeSectionName, option, tmp)
            option = "rootfolder0"
            tmp = cf.get("RootFolders", option)
            tmp = tmp.replace("my src", "src")
            cf.set(csnakeSectionName, option, tmp)
        # save the new context file
        contextNewFile = open(contextNewFileName, 'w')
        cf.write(contextNewFile)
        contextNewFile.close()
        
        # create GUI handler
        handler = csnGUIHandler.Handler()
        # load context
        context = handler.LoadContext(contextNewFileName)
        
        # set vars from context
        if buildType == "executable":
            exeName = projectName
            buildPath = "%s/executable" % context.buildFolder
        # ok, a bit fishy, I know the application name...
        elif buildType == "lib":
            exeName = projectName + "App_myApp"
            buildPath = "%s/library" % context.buildFolder

        # configure the project
        ret = handler.ConfigureProjectToBuildFolder( True )        
        # check that it worked
        assert ret == True, "CMake returned with an error message."
        
        # create compiler command
        compileArgList = []
        if( context.compilername.find("Visual Studio") != -1 ):
            # build path
            buildPath = "%s/%s" % (buildPath, projectName)
            # compiler
            compileArgList.append(context.idePath)
            # solution file
            solutionFile = handler.GetTargetSolutionPath()
            assert os.path.exists(solutionFile)
            compileArgList.append(solutionFile)
            # build mode
            mode = "%s|x64" % buildMode
            compileArgList.append("/build")
            compileArgList.append(mode)
        elif( context.compilername.find("KDevelop3") != -1 or
              context.compilername.find("Makefile") != -1 ):
            # build path
            buildPath = "%s/%s/%s" % (buildPath, buildMode, projectName)
            # make
            compileArgList.append("make")
            compileArgList.append("-s")
        
        # run compiler (cwd needed for make)
        ret = subprocess.call(compileArgList, cwd=buildPath)
        assert ret == 0, "The compiler returned with an error message."

        # check the built executable
        exeFilename = "%s/bin/%s/%s" % (context.buildFolder, buildMode, exeName)
        if( context.compilername.find("Visual Studio") != -1 ):
            exeFilename = "%s.exe" % (exeFilename)
        assert os.path.exists(exeFilename)
        
        # test the built executable
        ret = subprocess.call(exeFilename)
        assert ret == 6, "The generated executable did not return the correct result."

        # run tests with lib
        if buildType == "lib":
            # check the built test
            testName = projectName + "Tests"
            testExeFilename = "%s/bin/%s/%s" % (context.buildFolder, buildMode, testName)
            if( context.compilername.find("Visual Studio") != -1 ):
                testExeFilename = "%s.exe" % (testExeFilename)
            assert os.path.exists(testExeFilename)
            
            # run the test
            ret = subprocess.call(testExeFilename)
            assert ret == 0, "The generated test did not return the correct result."
        
        # clean up
        shutil.rmtree( csnProject.globalCurrentContext.buildFolder )
        
if __name__ == "__main__":
    unittest.main() 
