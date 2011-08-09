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
        assert Version("43.0.0") <= Version("43")
        assert Version("43.0.0") >= Version("43")
        assert Version("43.0.0") == Version("43")
        assert Version("43.0.0") != Version("43 beta")
        assert Version("45.1.beta") < Version("45.1.0")
        for numDecimals in range(0, 3):
            assert Version(Version("1.2.3.4.5.6.7/beta").GetString(numDecimals=numDecimals)) == Version("1.2.3.4.5.6.7/beta")
        assert Version("1.2 alpha").GetString(numDecimals=3) == "1.2.0.0-alpha"
        assert Version("1.2 alpha").GetString(numDecimals=2) == "1.2.0-alpha"
        assert Version("1.2 alpha").GetString(numDecimals=1) == "1.2-alpha"
        assert Version("1.2 alpha").GetString(numDecimals=0) == "1.2-alpha"

if __name__ == "__main__":
    unittest.main()

