# TestSuite: class to create all test suites to ease running them all at once.
import unittest
import xmlrunner

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
        """ Run the main suite. Output as xml. """
        # output file
        file = open("testslog.xml", 'w')
        # test runner
        res = xmlrunner.XMLTestRunner(file).run(self.suite)
        # close output
        file.close()
        # return result
        return res

if __name__ == "__main__":
    tests = AllTests();
    tests.run();
