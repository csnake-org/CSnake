## @package aboutTests
# Definition of the AboutTests class.
# \ingroup tests
import unittest
from about import About
import os

class AboutTests(unittest.TestCase):
    """ Tests for the About class. """

    def setUp(self):
        """ Run before test. """

    def tearDown(self):
        """ Run after test. """

    def testReadWrite(self):
        """ AboutTests: testReadWrite. """
        filename = "about_test.txt"
        # write the default about
        about = About()
        about.write(filename)
        # read it back
        about2 = About()
        about2.read(filename)
        # compare the 2 objects
        assert about == about2
        # clean up
        os.remove(filename)

if __name__ == "__main__":
    unittest.main()         
