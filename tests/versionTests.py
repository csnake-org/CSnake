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
        
        self.assertLess(Version("1.2.3"), Version("2.3.4"))
        self.assertGreater(Version("2.3.4"), Version("1.2.3"))
        
        sameVersion = ["43.0.0", "43.0", "43", ["43"], [43], [43, 0], [43, 0, 0]]
        for versionA in sameVersion:
            for versionB in sameVersion:
                versionAObj = Version(versionA)
                versionBObj = Version(versionB)
                versionStringPair = (json.dumps(versionA), json.dumps(versionB))
                self.assertLessEqual   (versionAObj, versionBObj, msg="Version(%s) should be <= Version(%s)" % versionStringPair)
                self.assertGreaterEqual(versionAObj, versionBObj, msg="Version(%s) should be >= Version(%s)" % versionStringPair)
                self.assertEqual       (versionAObj, versionBObj, msg="Version(%s) should be == Version(%s)" % versionStringPair)
                self.assertEqual(hash(versionAObj), hash(versionBObj), msg="hash(Version(%s)) should be == hash(Version(%s))" % versionStringPair)
        
        lowerVersionList = ["43 beta", "43.0.0 beta", ["43", "beta"], [43, "beta"], [43, "0", 0, "beta"]]
        higherVersionList = ["43", "43.0.0", ["43"], [43, ""], [43], [43, "0", 0]]
        for lowerVersion in lowerVersionList:
            for higherVersion in higherVersionList:
                lowerVersionObj = Version(lowerVersion)
                higherVersionObj = Version(higherVersion)
                versionStringPair = (json.dumps(lowerVersion), json.dumps(higherVersion))
                self.assertLess(lowerVersionObj, higherVersionObj, msg="%s should be < %s" % versionStringPair)
                self.assertNotEqual(lowerVersionObj, higherVersionObj, msg="%s should be != %s" % versionStringPair)
        
        # A list of arguments that should not be accepted by the Version constructor
        invalidConstructorArguments = ["", None, [], "beta", [""], [3, 2, 3, "dasklgjask-not-in-list-dljggaskdljkgsdl"],
            "dasklgjask-not-in-list-dljggaskdljkgsdl", "1.x.3"]
        for invalidConstructorArgument in invalidConstructorArguments:
            self.assertRaises(Exception, Version, invalidConstructorArgument)
        # Version constructor call without arguments should raise exception
        self.assertRaises(Exception, Version)
        
        for numDecimals in range(0, 10):
            self.assertEqual(Version(Version("1.2.3.4.5.6.7/beta").GetString(numDecimals=numDecimals)), Version("1.2.3.4.5.6.7/beta"))
        
        self.assertEqual(Version("1.2 alpha").GetString(numDecimals=3), "1.2.0.0-alpha")
        self.assertEqual(Version("1.2 alpha").GetString(numDecimals=2), "1.2.0-alpha")
        self.assertEqual(Version("1.2 alpha").GetString(numDecimals=1), "1.2-alpha")
        self.assertEqual(Version("1.2 alpha").GetString(numDecimals=0), "1.2-alpha")
        
        for versionString in ["43.0.1", "43.0.1.2-beta", "43.2.1", "47.1.39.144", "0.1.2.3.4.5.6"]:
            self.assertEqual(Version(versionString).GetString(), versionString)
            self.assertEqual(Version(versionString).GetString(0), versionString)
            self.assertEqual(Version(versionString).GetString(1), versionString)
            self.assertEqual(Version(versionString).GetString(2), versionString)

if __name__ == "__main__":
    unittest.main()

