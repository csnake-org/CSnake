## @package csnBuildTests
# Definition of the csnBuildTests class.
# \ingroup tests
import unittest
import os.path
import csnBuild
import csnProject
import csnGUIHandler
import shutil
import subprocess
from TestProjectConfig import TestProjectConfig
import csnContext

class csnBuildTests(unittest.TestCase):
    """
    Build tests: will try to configure, compile and test example project from the tests/data folder.
    Depends on local machine configuration, please create a tests/config/csnake_context.txt based on the
    following lines:

# Specific project settings
csnakefile = PATH_TO_CSNAKE/tests/data
instance = 
prebuiltBinariesFolder = 
kdevelopProjectFolder = 

# Toolkit settings
filter = *Demos
testrunnertemplate = xmlRunner.tpl
installfolder = PATH_TO_CSNAKE/tests
buildfolder = PATH_TO_CSNAKE/tests

# Compilation settings
compilername = Visual Studio 10 Win64
configurationname = DebugAndRelease

# General settings
pythonpath = C:/Program Files/Python27/python.exe
cmakepath = C:/Program Files (x86)/CMake 2.8/bin/cmake.exe
idepath = C:/Program Files (x86)/Microsoft Visual Studio 10.0/Common7/IDE/devenv.exe
version = 2.1

[RootFolders]
rootfolder0 = PATH_TO_CSNAKE/tests/data

[ThirdPartyFolders]
thirdpartyfolder0 = PATH_TO_CSNAKE/tests/data

[ThirdPartyBuildFolders]
thirdpartybuildfolder0 = PATH_TO_CSNAKE/tests
    """

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
        
    def testDummyExeBuild(self):
        """ testDummyExeBuild: test configuring and building the DummyExe project. """
        config = TestProjectConfig("DummyExe", "exe", "Release", 
                                   ["src"], "build",
                                   ["thirdParty"], ["build/thirdParty"],
                                   "src/DummyExe/csnDummyExe.py")
        self.build( config )
        
    def testDummyExeBuildWithSpace(self):
        """ testDummyExeBuild: test configuring and building the DummyExe project
        with spaces in folders. """
        config = TestProjectConfig("DummyExe", "exe", "Release", 
                                   ["my src"], "my build",
                                   ["third party"], ["my build/third party"],
                                   "my src/DummyExe/csnDummyExe.py")
        # Only for visual studio
        if( config.isVisualStudioConfig() == True ):
            self.build( config )
        
    def testDummyExeBuildMultiple(self):
        """ testDummyExeBuild: test configuring and building the DummyExe project
        with new syntax. """
        config = TestProjectConfig("DummyExe", "exe", "Release", 
                                   ["src", "src2"], "build",
                                   ["thirdParty"], ["build/thirdParty"],
                                   "src/DummyExe/csnDummyExe.py")
        self.build( config )
        
    def testDummyLibBuild(self):
        """ testDummyLibBuild: test configuring and building the DummyLib project. """
        config = TestProjectConfig("DummyLib", "lib", "Release", 
                                   ["src"], "build",
                                   ["thirdParty"], ["build/thirdParty"],
                                   "src/DummyLib/csnDummyLib.py")
        self.build( config )

    def testDummyLibBuildWithAPI(self):
        """ testDummyLibBuild: test configuring and building the DummyLib project. """
        config = TestProjectConfig("DummyLib", "lib", "Release", 
                                   ["src_api"], "build",
                                   ["thirdParty"], ["build/thirdParty"],
                                   "src_api/DummyLib/csnDummyLib.py")
        self.build( config )

    def testDummyLibBuildMultiple(self):
        """ testDummyLibBuildMul: test configuring and building the DummyLib project. """
        config = TestProjectConfig("DummyLib2", "lib", "Release", 
                                   ["src", "src2"], "build",
                                   ["thirdParty", "thirdParty2"], ["build/thirdParty", "build/thirdParty2"],
                                   "src2/DummyLib2/csnDummyLib2.py")
        self.build( config )


    def testDummyLibBuildWithSpace(self):
        """ testDummyLibBuildWithSpace: test configuring and building the DummyLib project with spaces in folders. """
        config = TestProjectConfig("DummyLib", "lib", "Release", 
                                   ["my src"], "my build",
                                   ["third party"], ["my build/third party"],
                                   "my src/DummyLib/csnDummyLib.py")
        # Only for visual studio
        if( config.isVisualStudioConfig() == True ):
            self.build( config )

    def build(self, testConfig):
        """ test configuring and building the input project. """
        # create the context file
        testConfig.createContext()
        
        # create GUI handler
        handler = csnGUIHandler.Handler()
        # load context
        context = handler.LoadContext(testConfig.getContextFileName())
        
        # configure and compile third parties
        ret = handler.ConfigureThirdPartyFolders()
        assert ret == True, "CMake returned with an error message while configuring the third parties."
        
        # compile third parties
        
        if( context.GetCompilername().find("Visual Studio") != -1 ):
            for index in range(0,context.GetNumberOfThirdPartyFolders()):
                # create compiler command
                compileArgList = []
                # compiler
                compileArgList.append(context.GetIdePath())
                # solution file
                solutionFile = "%s/CILAB_TOOLKIT.sln" % context.GetThirdPartyBuildFolderByIndex(index)
                assert os.path.exists(solutionFile), "The third party solution file does not exist."
                compileArgList.append(solutionFile)
                # build mode
                mode = "%s|x64" % testConfig.getBuildMode()
                compileArgList.append("/build")
                compileArgList.append(mode)
                # build path
                buildPath = testConfig.getTpBinDirs()[index]
                # run compiler
                ret = subprocess.call(compileArgList, cwd=buildPath)
                assert ret == 0, "The compiler returned with an error message while compiling the third parties."
            
        elif( context.GetCompilername().find("KDevelop3") != -1 or
              context.GetCompilername().find("Makefile") != -1 ):
            for index in range(0,context.GetNumberOfThirdPartyFolders()):
                # create compiler command
                compileArgList = []
                # build path
                buildPath = context.GetThirdPartyBuildFolderByIndex(index)
                # make
                compileArgList.append("make")
                compileArgList.append("-s")
                # run compiler (cwd needed for make)
                ret = subprocess.call(compileArgList, cwd=buildPath)
                assert ret == 0, "The compiler returned with an error message while compiling the third parties."
        
        # install files to bin folder
        ret = handler.InstallBinariesToBuildFolder()
        # check that it worked
        assert ret == True, "Installing binaries to build folder failed."
        
        # configure the project
        runCsnake = True
        ret = handler.ConfigureProjectToBuildFolder( runCsnake )        
        # check that it worked
        assert ret == True, "CMake returned with an error message while configuring the project."
        
        # compile project
        
        # create compiler command
        compileArgList = []
        if( context.GetCompilername().find("Visual Studio") != -1 ):
            # build path
            buildPath = "%s/%s" % (testConfig.getBuildPath(), testConfig.getName())
            # compiler
            compileArgList.append(context.GetIdePath())
            # solution file
            solutionFile = handler.GetTargetSolutionPath()
            assert os.path.exists(solutionFile), "The project solution file does not exist."
            compileArgList.append(solutionFile)
            # build mode
            mode = "%s|x64" % testConfig.getBuildMode()
            compileArgList.append("/build")
            compileArgList.append(mode)
        elif( context.GetCompilername().find("KDevelop3") != -1 or
              context.GetCompilername().find("Makefile") != -1 ):
            # build path
            buildPath = "%s/%s/%s" % (testConfig.getBuildPath(), testConfig.getBuildMode(), testConfig.getName())
            # make
            compileArgList.append("make")
            compileArgList.append("-s")
        
        # run compiler (cwd needed for make)
        ret = subprocess.call(compileArgList, cwd=buildPath)
        assert ret == 0, "The compiler returned with an error message while compiling the project."

        # check the built executable
        exeFilename = "%s/bin/%s/%s" % (context.GetBuildFolder(), testConfig.getBuildMode(), testConfig.getExeName())
        if( context.GetCompilername().find("Visual Studio") != -1 ):
            exeFilename = "%s.exe" % (exeFilename)
        assert os.path.exists(exeFilename)
        
        # test the built executable
        ret = subprocess.call(exeFilename)
        assert ret == 6, "The generated executable did not return the correct result."

        # run tests with lib
        if testConfig.getType() == "lib":
            # check the built test
            testName = testConfig.getName() + "Tests"
            testExeFilename = "%s/bin/%s/%s" % (context.GetBuildFolder(), testConfig.getBuildMode(), testName)
            if( context.GetCompilername().find("Visual Studio") != -1 ):
                testExeFilename = "%s.exe" % (testExeFilename)
            assert os.path.exists(testExeFilename)
            
            # run the test
            ret = subprocess.call(testExeFilename)
            assert ret == 0, "The generated test did not return the correct result."
        
        # clean up
        shutil.rmtree( csnProject.globalCurrentContext.GetBuildFolder() )
        os.remove(testConfig.getContextFileName())
        
if __name__ == "__main__":
    unittest.main() 
