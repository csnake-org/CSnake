# Unit tests for the csnInstall class
import unittest
import csnContext
import csnProject
import shutil
import os.path
import csnUtility

class csnInstallTests(unittest.TestCase):
    
    def setUp(self):
        """ Run before test. """
        # load fake context
        self.context = csnContext.Load("config/csnake_context.txt")
        # change the build folder
        self.context.buildFolder = self.context.buildFolder + "/bin"
        # set it as global context
        csnProject.globalCurrentContext = self.context
        # logging init
        csnUtility.InitialiseLogging()

    def tearDown(self):
        """ Run after test. """
        csnProject.globalCurrentContext = None

    def testInstall(self):
        """ csnInstallTests: test the installation of files. """
        # dummyLib project
        dummyInstall = csnProject.Project("DummyInstall", "library")
        dummyInstall.AddFilesToInstall(dummyInstall.Glob("AllTests.bat"), _debugOnly = 1, _WIN32 = 1, _NOT_WIN32 = 1)
        dummyInstall.AddFilesToInstall(dummyInstall.Glob("AllTests.sh"), _releaseOnly = 1, _WIN32 = 1, _NOT_WIN32 = 1)
        dummyInstall.installManager.InstallBinariesToBuildFolder()
        # check presence of the files
        assert os.path.exists("bin/bin/Debug/AllTests.bat"), "File not installed in Debug mode."
        assert os.path.exists("bin/bin/Release/AllTests.sh"), "File not installed in Release mode."
        # clean up
        shutil.rmtree( csnProject.globalCurrentContext.buildFolder )

    def testWinSwitch(self):
        """ csnInstallTests: test install files with windows switch. """
        location = "./Install"
        project = csnProject.Project("TestProject", "dll")
        project.AddFilesToInstall(["Hello.cpp"], location, _WIN32 = 1)
        project.AddFilesToInstall(["Bye.h"], location, _NOT_WIN32 = 1)
        # _WIN32 case
        if( self.context.compilername.find("Visual Studio") != -1 ):
            assert project.installManager.filesToInstall["Release"][location] == ["Hello.cpp"]
            assert project.installManager.filesToInstall["Debug"][location] == ["Hello.cpp"]
        # _NOT_WIN32 case
        elif( self.context.compilername.find("KDevelop3") != -1 or
              self.context.compilername.find("Makefile") != -1 ):
            assert project.installManager.filesToInstall["Release"][location] == ["Bye.h"]
            assert project.installManager.filesToInstall["Debug"][location] == ["Bye.h"]
        
if __name__ == "__main__":
    unittest.main()
