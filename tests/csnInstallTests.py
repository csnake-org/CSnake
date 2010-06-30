# Unit tests for the csnInstall class
import unittest
import csnContext
import csnProject
import shutil
import os.path
import csnUtility
import logging.config

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
        logging.config.fileConfig(csnUtility.GetRootOfCSnake() + "/resources/logging.conf")

    def tearDown(self):
        """ Run after test. """
        csnProject.globalCurrentContext = None

    def testInstall(self):
        """ Test the installation of files. """
        # dummyLib project
        dummyInstall = csnProject.Project("DummyInstall", "library")
        dummyInstall.AddFilesToInstall(["AllTests.bat"], _debugOnly = 1, _WIN32 = 1, _NOT_WIN32 = 1)
        dummyInstall.AddFilesToInstall(["AllTests.bat"], _releaseOnly = 1, _WIN32 = 1, _NOT_WIN32 = 1)
        dummyInstall.installManager.InstallBinariesToBuildFolder()
        # check presence of the files
        assert os.path.exists("bin/bin/Debug/AllTests.bat"), "File not installed in Debug mode."
        assert os.path.exists("bin/bin/Release/AllTests.bat"), "File not installed in Release mode."
        # clean up
        shutil.rmtree( csnProject.globalCurrentContext.buildFolder )

if __name__ == "__main__":
    unittest.main()
