## @package versionTests
# Definition of the tests for the Version class.
# \ingroup tests
import unittest
import json
from csnVersion import Version

class VersionTests(unittest.TestCase):
    """ Tests for the Version class. """
    
    def setUp(self):
        """ Run before test. """
    
    def tearDown(self):
        """ Run after test. """
    
    def testVersion(self):
        """ AboutTests: testVersion. """
        
        assert Version("1.2.3") < Version("2.3.4")
        assert Version("2.3.4") > Version("1.2.3")
        
        sameVersion = ["43.0.0", "43.0", "43", ["43"], [43], [43, 0], [43, 0, 0]]
        for versionA in sameVersion:
            for versionB in sameVersion:
                versionAObj = Version(versionA)
                versionBObj = Version(versionB)
                versionStringPair = (json.dumps(versionA), json.dumps(versionB))
                assert versionAObj <= versionBObj, "Version(%s) should be <= Version(%s)" % versionStringPair
                assert versionAObj >= versionBObj, "Version(%s) should be >= Version(%s)" % versionStringPair
                assert versionAObj == versionBObj, "Version(%s) should be == Version(%s)" % versionStringPair
        
        lowerVersionList = ["43 beta", "43.0.0 beta", ["43", "beta"], [43, "beta"], [43, "0", 0, "beta"]]
        higherVersionList = ["43", "43.0.0", ["43"], [43, ""], [43], [43, "0", 0]]
        for lowerVersion in lowerVersionList:
            for higherVersion in higherVersionList:
                lowerVersionObj = Version(lowerVersion)
                higherVersionObj = Version(higherVersion)
                versionStringPair = (json.dumps(lowerVersion), json.dumps(higherVersion))
                assert lowerVersionObj < higherVersionObj, "%s should be < %s" % versionStringPair
                assert lowerVersionObj != higherVersionObj, "%s should be != %s" % versionStringPair
        
        # A list of arguments that should not be accepted by the Version constructor
        invalidConstructorArguments = ["", None, [], "beta", [""], [3, 2, 3, "dasklgjask-not-in-list-dljggaskdljkgsdl"],
            "dasklgjask-not-in-list-dljggaskdljkgsdl", "1.x.3"]
        for invalidConstructorArgument in invalidConstructorArguments:
            self.assertRaises(Exception, Version, invalidConstructorArgument)
        # Version constructor call without arguments should raise exception
        self.assertRaises(Exception, Version)
        
        for numDecimals in range(0, 3):
            assert Version(Version("1.2.3.4.5.6.7/beta").GetString(numDecimals=numDecimals)) == Version("1.2.3.4.5.6.7/beta")
        
        assert Version("1.2 alpha").GetString(numDecimals=3) == "1.2.0.0-alpha"
        assert Version("1.2 alpha").GetString(numDecimals=2) == "1.2.0-alpha"
        assert Version("1.2 alpha").GetString(numDecimals=1) == "1.2-alpha"
        assert Version("1.2 alpha").GetString(numDecimals=0) == "1.2-alpha"

if __name__ == "__main__":
    unittest.main()

