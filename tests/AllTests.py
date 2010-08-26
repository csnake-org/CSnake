# TestSuite: class to create all test suites to ease running them all at once.
import unittest
import xmlrunner
import sys
import getopt

from csnBuildTests import csnBuildTests
from csnGUIHandlerTests import csnGUIHandlerTests
from csnProjectTests import csnProjectTests
from csnUtilityTests import csnUtilityTests
from csnContextConverterTests import csnContextConverterTests
from aboutTests import AboutTests
from csnInstallTests import csnInstallTests

class AllTests:
    def __init__(self, outputFileName):
        ''' 
        Initialise the class: create test suite.
        @param _outputFileName: The name of the output file.
        '''
        # create suites from unit tests
        buildSuite = unittest.TestLoader().loadTestsFromTestCase(csnBuildTests)
        uiSuite = unittest.TestLoader().loadTestsFromTestCase(csnGUIHandlerTests)
        csnProjectSuite = unittest.TestLoader().loadTestsFromTestCase(csnProjectTests)
        csnUtilitySuite = unittest.TestLoader().loadTestsFromTestCase(csnUtilityTests)
        csnContextConverterSuite = unittest.TestLoader().loadTestsFromTestCase(csnContextConverterTests)
        aboutSuite = unittest.TestLoader().loadTestsFromTestCase(AboutTests)
        installSuite = unittest.TestLoader().loadTestsFromTestCase(csnInstallTests)
        # main suite
        self.__suite = unittest.TestSuite([
             buildSuite, uiSuite, csnProjectSuite, 
             csnUtilitySuite, csnContextConverterSuite,
             aboutSuite, installSuite])
        # output file name
        self.__outputFileName = outputFileName
        
    def run(self):
        """ Run the main suite. Output as xml. """
        # output file
        outputFile = open(self.__outputFileName, 'w')
        # test runner
        runner = xmlrunner.XMLTestRunner(outputFile)
        # run tests
        result = runner.run(self.__suite)
        # close output
        outputFile.close()
        # return result (1 for success)
        return result.wasSuccessful()
 
def usage():
    ''' Usage for main method.'''
    print "Usage: ", sys.argv[0], " [-o filename]"
    print "-h: help."
    print "-o: test output file name, default to 'testslog.xml'."
   
def main():
    '''
    Main method to run all tests.
    @param argv: command line arguments; first should be the tests output file name.
    '''
    # extract the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:", ["help", "output="]) #@UnusedVariable
    except getopt.GetoptError:
        usage()
        return 2
    # process the command line arguments
    outputFileName = "testslog.xml"
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return 0
        elif opt == '-o':
            outputFileName = arg
    # run the tests
    tests = AllTests(outputFileName)
    res = tests.run()
    if res:
        print "\n== All Tests Successful! =="
    else:
        print "\n== Failed Tests! =="
    # return result (0 for success)
    return not res

if __name__ == "__main__":
    sys.exit(main())
