## @package AllTests
# Definition of the AllTests class.
# \ingroup tests
import getopt
import os
import sys
import unittest
import xmlrunner

import csnUtility

from csnBuildTests import csnBuildTests
from csnGUIHandlerTests import csnGUIHandlerTests
from csnProjectTests import csnProjectTests
from csnUtilityTests import csnUtilityTests
from csnContextTests import csnContextTests
from csnGUIOptionsTests import csnGUIOptionsTests
from aboutTests import AboutTests
from versionTests import VersionTests
from csnInstallTests import csnInstallTests
from csnCilabTests import csnCilabTests

def CreateConfigFileLinux():
    # find out config values
    csnakeTestPath = "/".join(os.path.realpath(__file__).split("/")[0:-1])
    csnakeTestDataPath = os.path.join(csnakeTestPath, "data")
    pythonPath = csnUtility.SearchUnixProgramPath("python")
    cmakePath = csnUtility.SearchUnixProgramPath("cmake")
    values = {
            "csnakefile"            : csnakeTestDataPath,
            "instance"              : "",
            "filter"                : "*Demos",
            "testrunnertemplate"    : "xmlRunner.tpl",
            "installfolder"         : csnakeTestPath,
            "buildfolder"           : csnakeTestPath,
            "compiler"              : "Unix Makefiles",
            "configurationname"     : "Release",
            "pythonpath"            : pythonPath,
            "cmakepath"             : cmakePath,
            "idepath"               : ".",
            "version"               : "2.1",
            "rootfolder0"           : csnakeTestDataPath,
            "thirdpartyrootfolder"  : csnakeTestDataPath,
            "thirdpartybuildfolder" : csnakeTestPath
        }
    
    # read config file template
    f = open(os.path.join(csnakeTestPath, "csnake_context.txt"), 'r')
    configFileString = f.read()
    f.close()
    
    # replace values
    for key, value in values.items():
        configFileString = configFileString.replace("@%s@" % key, value)
    
    # write config file
    configdir = os.path.join(csnakeTestPath, "config")
    if not os.path.isdir(configdir):
        if os.path.exists(configdir):
            print 'ERROR: The path "%s" exists, but is not a directory. So I cannot create any files in it nor create that directory.' % configdir
            return -1
        else:
            os.makedirs(configdir)
    f = open(os.path.join(configdir, "csnake_context.txt"), 'w')
    f.write(configFileString)
    f.close
    return 0

class AllTests:
    """ Class to create all test suites to ease running them all at once. """
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
        csnContextSuite = unittest.TestLoader().loadTestsFromTestCase(csnContextTests)
        csnGUIOptionsSuite = unittest.TestLoader().loadTestsFromTestCase(csnGUIOptionsTests)
        aboutSuite = unittest.TestLoader().loadTestsFromTestCase(AboutTests)
        versionSuite = unittest.TestLoader().loadTestsFromTestCase(VersionTests)
        installSuite = unittest.TestLoader().loadTestsFromTestCase(csnInstallTests)
        cilabSuite = unittest.TestLoader().loadTestsFromTestCase(csnCilabTests)
        # main suite
        self.__suite = unittest.TestSuite([
             buildSuite, uiSuite, csnProjectSuite, 
             csnUtilitySuite, csnContextSuite, csnGUIOptionsSuite,
             aboutSuite, versionSuite, installSuite, cilabSuite])
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
    print "-c / --createConfigLinux: Create config file for linux."
    print "-h: help."
    print "-o: test output file name, default to 'testslog.xml'."
   
def main():
    '''
    Main method to run all tests.
    @param argv: command line arguments; first should be the tests output file name.
    '''
    # extract the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cho:", ["createConfigLinux", "help", "output="]) #@UnusedVariable
    except getopt.GetoptError:
        usage()
        return 2
    # process the command line arguments
    outputFileName = "testslog.xml"
    for opt, arg in opts:
        if opt in ("-c", "--createConfigLinux"):
            return CreateConfigFileLinux()
        elif opt in ("-h", "--help"):
            usage()
            return 0
        elif opt == '-o':
            outputFileName = arg
    # run the tests
    tests = AllTests(outputFileName)
    res = tests.run()
    print "\nTests results can be found in '%s'." % outputFileName
    if res:
        print "\n== All Tests Successful! =="
    else:
        print "\n== Failed Tests! =="
    # return result (0 for success)
    return not res

if __name__ == "__main__":
    sys.exit(main())
