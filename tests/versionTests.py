## @package versionTests
# Definition of the tests for the Version class.
# \ingroup tests
import unittest
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
        
        sameVersion = [Version(versionString = "43.0.0"),
            Version(versionString = "43.0"),
            Version(versionString = "43"),
            Version(versionArray = ["43"]),
            Version(versionArray = [43]),
            Version("", [43]),
            Version(None, [43]),
            Version(versionArray = [43, 0]),
            Version(versionArray = [43, 0, 0])]
        for versionA in sameVersion:
            for versionB in sameVersion:
                assert versionA <= versionB, "%s should be <= %s" % (versionA.GetString(), versionB.GetString())
                assert versionA >= versionB, "%s should be >= %s" % (versionA.GetString(), versionB.GetString())
                assert versionA == versionB, "%s should be == %s" % (versionA.GetString(), versionB.GetString())
        
        lowerVersionList = [Version("43 beta"), Version("43.0.0 beta"), Version(versionArray=["43", "beta"]),
                Version(versionArray=[43, "beta"]), Version(versionArray=[43, "0", 0, "beta"])]
        higherVersionList = [Version("43"), Version("43.0.0"), Version(versionArray=["43"]), Version(versionArray=[43, ""]),
                Version(versionArray=[43]), Version(versionArray=[43, "0", 0])]
        for lowerVersion in lowerVersionList:
            for higherVersion in higherVersionList:
                assert lowerVersion < higherVersion, "%s should be < %s" % (lowerVersion.GetString(), higherVersion.GetString())
                assert lowerVersion != higherVersion, "%s should be != %s" % (lowerVersion.GetString(), higherVersion.GetString())
        
        self.awaitException('Version("")')
        self.awaitException('Version(None)')
        self.awaitException('Version()')
        self.awaitException('Version(versionString = None, versionArray = None)')
        self.awaitException('Version(versionArray = None)')
        self.awaitException('Version(versionArray = [])')
        self.awaitException('Version(versionString = None)')
        self.awaitException('Version(versionArray = ["beta"])')
        self.awaitException('Version(versionArray = [""])')
        self.awaitException('Version(versionArray = [3, 2, 3, "dasklgjask-not-in-list-dljggaskdljkgsdl"])')
        self.awaitException('Version(versionString = "4", versionArray = [3])')
        
        for numDecimals in range(0, 3):
            assert Version(Version("1.2.3.4.5.6.7/beta").GetString(numDecimals=numDecimals)) == Version("1.2.3.4.5.6.7/beta")
        
        assert Version("1.2 alpha").GetString(numDecimals=3) == "1.2.0.0-alpha"
        assert Version("1.2 alpha").GetString(numDecimals=2) == "1.2.0-alpha"
        assert Version("1.2 alpha").GetString(numDecimals=1) == "1.2-alpha"
        assert Version("1.2 alpha").GetString(numDecimals=0) == "1.2-alpha"
    
    def awaitException(self, code):
        gotException = False
        try:
            exec code
        except:
            gotException = True
        assert gotException, "Should have received an exception"
        
if __name__ == "__main__":
    unittest.main()

