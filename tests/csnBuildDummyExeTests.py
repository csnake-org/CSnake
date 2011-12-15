## @package csnBuildDummyExeTests
# Definition of the csnBuildDummyExeTests class.
# \ingroup tests
import unittest
from TestProjectConfig import TestProjectConfig
import BuildTest

class csnBuildDummyExeTests(unittest.TestCase):
    """ Build dummy exe tests. """

    def setUp(self):
        """ Run before test. """

    def tearDown(self):
        """ Run after test. """

    def testDummyExeBuild(self):
        """ testDummyExeBuild: test configuring and building the DummyExe project. """
        config = TestProjectConfig("DummyExe", "exe", "Release", 
                                   ["src"], "build",
                                   ["thirdParty"], ["build/thirdParty"],
                                   "src/DummyExe/csnDummyExe.py")
        BuildTest.testBuild( config )
        
    def testDummyExeBuildWithAPI(self):
        """ testDummyExeBuild: test configuring and building the DummyExe project. """
        config = TestProjectConfig("DummyExe", "exe", "Release", 
                                   ["src_api"], "build",
                                   ["thirdParty_api"], ["build/thirdParty"],
                                   "src_api/DummyExe/csnDummyExe.py")
        BuildTest.testBuild( config )
        
    def testDummyExeBuildMix(self):
        """ testDummyExeBuild: test configuring and building the DummyExe project. """
        config = TestProjectConfig("DummyExe", "exe", "Release", 
                                   ["src_api"], "build",
                                   ["thirdParty"], ["build/thirdParty"],
                                   "src_api/DummyExe/csnDummyExe.py")
        BuildTest.testBuild( config )

    def testDummyExeBuildMix2(self):
        """ testDummyExeBuild: test configuring and building the DummyExe project. """
        config = TestProjectConfig("DummyExe", "exe", "Release", 
                                   ["src"], "build",
                                   ["thirdParty_api"], ["build/thirdParty"],
                                   "src/DummyExe/csnDummyExe.py")
        BuildTest.testBuild( config )

    def testDummyExeBuildMix3(self):
        """ testDummyExeBuild: test configuring and building the DummyExe project. """
        config = TestProjectConfig("DummyExe", "exe", "Release", 
                                   ["src_mix"], "build",
                                   ["thirdParty_api"], ["build/thirdParty"],
                                   "src_mix/DummyExe/csnDummyExe.py")
        BuildTest.testBuild( config )

    def testDummyExeBuildWithSpace(self):
        """ testDummyExeBuild: test configuring and building the DummyExe project
        with spaces in folders. """
        config = TestProjectConfig("DummyExe", "exe", "Release", 
                                   ["my src"], "my build",
                                   ["third party"], ["my build/third party"],
                                   "my src/DummyExe/csnDummyExe.py")
        # Only for visual studio
        if( config.isVisualStudioConfig() == True ):
            BuildTest.testBuild( config )
        
    def testDummyExeBuildMultiple(self):
        """ testDummyExeBuild: test configuring and building the DummyExe project
        with new syntax. """
        config = TestProjectConfig("DummyExe", "exe", "Release", 
                                   ["src", "src2"], "build",
                                   ["thirdParty"], ["build/thirdParty"],
                                   "src/DummyExe/csnDummyExe.py")
        BuildTest.testBuild( config )

if __name__ == "__main__":
    unittest.main() 
