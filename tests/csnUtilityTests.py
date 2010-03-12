# Unit tests for the csnUtility methods
import unittest
import csnUtility

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

if __name__ == "__main__":
    unittest.main() 