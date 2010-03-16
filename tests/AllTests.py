# TestSuite: class to create all test suites to ease running them all at once.
import unittest
import xmlrunner
import sys

from csnBuildTests import csnBuildTests
from csnGUIHandlerTests import csnGUIHandlerTests
from csnProjectTests import csnProjectTests
from csnUtilityTests import csnUtilityTests

class AllTests:
    def __init__(self, _outputFileName):
        ''' 
        Initialise the class: create test suite.
        @param _outputFileName: The name of the output file.
        '''
        # create suites from unit tests
        buildSuite = unittest.TestLoader().loadTestsFromTestCase(csnBuildTests)
        uiSuite = unittest.TestLoader().loadTestsFromTestCase(csnGUIHandlerTests)
        csnProjectSuite = unittest.TestLoader().loadTestsFromTestCase(csnProjectTests)
        csnUtilitySuite = unittest.TestLoader().loadTestsFromTestCase(csnUtilityTests)
        # main suite
        self.suite = unittest.TestSuite([buildSuite, uiSuite, csnProjectSuite, csnUtilitySuite])
        # output file name
        self.outputFileName = _outputFileName
        
    def run(self):
        """ Run the main suite. Output as xml. """
        # output file
        outputFile = open(self.outputFileName, 'w')
        # test runner
        res = xmlrunner.XMLTestRunner(outputFile).run(self.suite)
        # close output
        outputFile.close()
        # return result
        return res
    
def main(argv):
    '''
    Main method to run all tests.
    @param argv: command line arguments; first should be the tests output file name.
    '''
    tests = AllTests(argv[1])
    return tests.run()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
