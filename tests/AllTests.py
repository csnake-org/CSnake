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
from csnAPITests import csnAPITests
from csnBuildDummyLibTests import csnBuildDummyLibTests
from csnBuildDummyExeTests import csnBuildDummyExeTests

def CreateConfigFile():
    # find out config values
    csnakeTestPath = os.path.dirname(os.path.realpath(__file__))
    csnakeTestDataPath = os.path.join(csnakeTestPath, "data")
    if not csnUtility.IsWindowsPlatform():
        csnakeTestPath = "/" + csnakeTestPath
        csnakeTestDataPath = "/" + csnakeTestDataPath
        compiler = "Unix Makefiles"
        idepath = "."
    else:
        # cmake does not like backslashes
        csnakeTestPath = csnakeTestPath.replace('\\', '/')
        csnakeTestDataPath = csnakeTestDataPath.replace('\\', '/')
        compiler = "Visual Studio 15 Win64"
        idepath = csnUtility.GetDefaultVisualStudioPath(compiler)
    values = {
            "csnakefile"            : csnakeTestDataPath,
            "instance"              : "",
            "filter"                : "*Demos",
            "testrunnertemplate"    : "xmlRunner.tpl",
            "installfolder"         : csnakeTestPath,
            "buildfolder"           : csnakeTestPath,
            "compiler"              : compiler,
            "configurationname"     : "Release",
            "pythonpath"            : csnUtility.GetDefaultPythonPath(),
            "cmakepath"             : csnUtility.GetDefaultCMakePath(),
            "idepath"               : idepath,
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
    def __init__(self, mode, outputFileName):
        ''' 
        Initialise the class: create test suite.
        @param _mode: The output mode: text|xml.
        @param _outputFileName: The name of the output file.
        '''
        # create suites from unit tests
        tests = []
        tests.append( unittest.TestLoader().loadTestsFromTestCase(csnAPITests) )
        tests.append( unittest.TestLoader().loadTestsFromTestCase(csnBuildTests) )
        tests.append( unittest.TestLoader().loadTestsFromTestCase(csnCilabTests) )
        tests.append( unittest.TestLoader().loadTestsFromTestCase(csnContextTests) )
        tests.append( unittest.TestLoader().loadTestsFromTestCase(csnGUIHandlerTests) )
        tests.append( unittest.TestLoader().loadTestsFromTestCase(csnGUIOptionsTests) )
        tests.append( unittest.TestLoader().loadTestsFromTestCase(csnInstallTests) )
        tests.append( unittest.TestLoader().loadTestsFromTestCase(csnProjectTests) )
        tests.append( unittest.TestLoader().loadTestsFromTestCase(csnUtilityTests) )
        tests.append( unittest.TestLoader().loadTestsFromTestCase(AboutTests) )
        tests.append( unittest.TestLoader().loadTestsFromTestCase(VersionTests) )
        # long...
        tests.append( unittest.TestLoader().loadTestsFromTestCase(csnBuildDummyLibTests) )
        tests.append( unittest.TestLoader().loadTestsFromTestCase(csnBuildDummyExeTests) )
        # main suite
        self.__suite = unittest.TestSuite(tests)
        # output mode
        self.__mode = mode
        # output file name
        self.__outputFileName = outputFileName
        
    def run(self):
        """ Run the main suite. """
        # output
        if len(self.__outputFileName) != 0:
            output = open(self.__outputFileName, 'w')
        else:
            output = sys.stderr
        # test runner
        if self.__mode == "xml":
            runner = xmlrunner.XMLTestRunner(output)
        else:
            runner = unittest.TextTestRunner(output)
        # run tests
        result = runner.run(self.__suite)
        # close output
        if len(self.__outputFileName) != 0:
            output.close()
        # return result (1 for success)
        return result.wasSuccessful()
 
def usage():
    ''' Usage for main method.'''
    print "Usage: ", sys.argv[0], " [-o filename -l -m xml]"
    print "-h / --help: help."
    print "-l / --localConfig: Use a local config file (in 'tests/config/csnake_context.txt', if not present, automatically created)."
    print "-m / --mode: test output mode: xml|txt (default to txt)."
    print "-o / --output: test output file name (if not present, default to stderr)."
   
def main():
    '''
    Main method to run all tests.
    @param argv: command line arguments; first should be the tests output file name.
    '''
    # extract the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlm:o:", ["help", "localConfig", "mode=", "output="]) #@UnusedVariable
    except getopt.GetoptError:
        usage()
        return 2
    # process the command line arguments
    outputFileName = ""
    localConfig = False
    mode = "txt"
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return 0
        elif opt in ("-l", "--localConfig"):
            localConfig = True
        elif opt in ('-m', "--mode"):
            mode = arg
        elif opt in ('-o', "--output"):
            outputFileName = arg
    # create config if needed
    if not localConfig:
        CreateConfigFile()
    # run the tests
    tests = AllTests(mode, outputFileName)
    res = tests.run()
    # print summary if all goes in file
    if len( outputFileName ) != 0:
        print "\nTests results can be found in '%s'." % outputFileName
        if res:
            print "\n== All Tests Successful! =="
        else:
            print "\n== Failed Tests! =="
    # return result (0 for success)
    return not res

if __name__ == "__main__":
    sys.exit(main())
