# TestSuite: class to create all test suites to ease running them all at once.
import unittest

from csnBuildTests import csnBuildTests
from csnGUIHandlerTests import csnGUIHandlerTests
from csnProjectTests import csnProjectTests
from csnUtilityTests import csnUtilityTests

class AllTests:
    def __init__(self):
        """ Initialise the class: create test suite. """
        # create suites from unit tests
        buildSuite = unittest.TestLoader().loadTestsFromTestCase(csnBuildTests)
        uiSuite = unittest.TestLoader().loadTestsFromTestCase(csnGUIHandlerTests)
        csnProjectSuite = unittest.TestLoader().loadTestsFromTestCase(csnProjectTests)
        csnUtilitySuite = unittest.TestLoader().loadTestsFromTestCase(csnUtilityTests)
        # main suite
        self.suite = unittest.TestSuite([buildSuite, uiSuite, csnProjectSuite, csnUtilitySuite])

    def run(self):
        """ Run the main suite. """
        return unittest.TextTestRunner(verbosity=2).run(self.suite)

if __name__ == "__main__":
    tests = AllTests();
    tests.run();
