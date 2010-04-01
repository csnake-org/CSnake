# Unit tests for the csnUtility methods
import unittest
import csnUtility
import os

class csnUtilityTests(unittest.TestCase):
    
    def testNormalizePath(self):
        """ csnUtilityTests: test NormalizePath function. """
        refString = "c:/hallo"
        testString1 = "c:/hallo"
        assert refString == csnUtility.NormalizePath(testString1)
        testString2 = "c:\\hallo"
        assert refString == csnUtility.NormalizePath(testString2)

    def testRemovePrefixFromPath(self):
        """ csnUtilityTests: test RemovePrefixFromPath function. """
        path = "c:/one/two/three"
        prefix = "c:"
        subString = "/one/two/three"
        assert subString == csnUtility.RemovePrefixFromPath(path, prefix)

    def testHasBackSlash(self):
        """ csnUtilityTests: test HasBackSlash function. """
        assert csnUtility.HasBackSlash("c:\\hallo")
        assert not csnUtility.HasBackSlash("c://hallo")
        
    def testCorrectPath(self):
        """ csnUtilityTests: test CorrectPath function. """
        refPathRoot = "src/DummyLib"
        refPath = os.path.normpath( refPathRoot + "/libmodules" )
        
        testPath1 = "src/DummyLib/libmodules"
        assert csnUtility.CorrectPath(testPath1) == refPath        
        testPath2 = "src/DummyLib/liBmoDules"
        assert csnUtility.CorrectPath(testPath2) == refPath        
        testPath3 = "src/DuMMyLib/libmodules"
        assert csnUtility.CorrectPath(testPath3) == refPath        
        refPath4 = os.path.normpath( "src/DummyLib/doEsnoTexist" )
        testPath4 = "src/DuMMyLib/doEsnoTexist"
        assert csnUtility.CorrectPath(testPath4) == refPath4        
        refPath5 = os.path.normpath( "doEs/nOt/eXist" )
        testPath5 = "doEs/nOt/eXist"
        assert csnUtility.CorrectPath(testPath5) == refPath5        

if __name__ == "__main__":
    unittest.main() 