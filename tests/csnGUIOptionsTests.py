## @package csnGUIOptionsTests
# Definition of the csnGUIOptionsTests class.
# \ingroup tests
import unittest
import os
from csnGUIOptions import Options
import shutil

class csnGUIOptionsTests(unittest.TestCase):
    """ Unit tests for the csnContextConverter methods. """
    
    def setUp(self):
        """ Run before test. """

    def tearDown(self):
        """ Run after test. """

    def testReadOptions00(self):
        ''' csnContextTests: test read from options v0.0. '''
        # test the options conversion
        self.ReadOptionsTest(0.0, "options00a.txt")

    def testReadOptions10(self):
        ''' csnContextTests: test read from options v1.0. '''
        # test the options conversion
        self.ReadOptionsTest(1.0, "options10a.txt")

    def testReadOptions11(self):
        ''' csnContextTests: test read from options v1.1. '''
        # test the options conversion
        self.ReadOptionsTest(1.1, "options11a.txt")

    def ValuesTest(self, version, options):
        self.assertEqual( options.GetAskToLaunchIDE(), True )
        self.assertEqual( options.GetContextFilename(), "E:\\devel\\src\\toolkit\\module_clean.CSnakeGUI" )
        if version >= 1.1:
            self.assertEqual( options.GetRecentContextPath(0), "E:\\devel\\src\\toolkit\\clean.CSnakeGUI" )
            self.assertEqual( options.GetRecentContextPath(1), "E:\\devel\\src\\toolkit\\devel.CSnakeGUI" )
            self.assertEqual( options.GetRecentContextPath(2), "E:\\devel\\src\\toolkit\\stable.CSnakeGUI" )
        
    def ReadOptionsTest(self, version, inputFilename):
        ''' csnContextTests: test read options. '''
        # create a copy of the input file
        filename = "test_%s" % inputFilename
        shutil.copy(inputFilename, filename)
        
        # try to read the file
        options = Options()
        options.Load(filename)
        
        # test values 
        self.ValuesTest(version, options)
        
        # save it
        newFilename = "new_%s" % filename
        options.Save(newFilename)
        
        # re-read
        newOptions = Options()
        newOptions.Load(newFilename)
        
        # test values 
        self.ValuesTest(version, newOptions)

        # clean up
        os.remove(filename)
        os.remove(newFilename)
        backupFilename = "%s.bk" % filename
        if os.path.isfile(backupFilename):
            os.remove(backupFilename)
       
if __name__ == "__main__":
    unittest.main() 
