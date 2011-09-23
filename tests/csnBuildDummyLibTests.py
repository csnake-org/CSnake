## @package csnBuildTests
# Definition of the csnBuildTests class.
# \ingroup tests
import unittest
from TestProjectConfig import TestProjectConfig
import BuildTest

class csnBuildDummyLibTests(unittest.TestCase):
    """ Build dummy lib tests. """

    def setUp(self):
        """ Run before test. """

    def tearDown(self):
        """ Run after test. """

    def testDummyLibBuild(self):
        """ testDummyLibBuild: test configuring and building the DummyLib project. """
        config = TestProjectConfig("DummyLib", "lib", "Release", 
                                   ["src"], "build",
                                   ["thirdParty"], ["build/thirdParty"],
                                   "src/DummyLib/csnDummyLib.py")
        BuildTest.testBuild( config )

    def testDummyLibBuildWithAPI(self):
        """ testDummyLibBuild: test configuring and building the DummyLib project. """
        config = TestProjectConfig("DummyLib", "lib", "Release", 
                                   ["src_api"], "build",
                                   ["thirdParty_api"], ["build/thirdParty"],
                                   "src_api/DummyLib/csnDummyLib.py")
        BuildTest.testBuild( config )

    def testDummyLibBuildMultiple(self):
        """ testDummyLibBuildMul: test configuring and building the DummyLib project. """
        config = TestProjectConfig("DummyLib2", "lib", "Release", 
                                   ["src", "src2"], "build",
                                   ["thirdParty", "thirdParty2"], ["build/thirdParty", "build/thirdParty2"],
                                   "src2/DummyLib2/csnDummyLib2.py")
        BuildTest.testBuild( config )

    def testDummyLibBuildWithSpace(self):
        """ testDummyLibBuildWithSpace: test configuring and building the DummyLib project with spaces in folders. """
        config = TestProjectConfig("DummyLib", "lib", "Release", 
                                   ["my src"], "my build",
                                   ["third party"], ["my build/third party"],
                                   "my src/DummyLib/csnDummyLib.py")
        # Only for visual studio
        if( config.isVisualStudioConfig() == True ):
            BuildTest.testBuild( config )
        
if __name__ == "__main__":
    unittest.main() 
