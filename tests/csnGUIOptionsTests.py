# Unit tests for the csnContextConverter methods
import unittest
import os
import csnGUIOptions
from csnGUIOptions import Options

class csnGUIOptionsTests(unittest.TestCase):

    def testReadOptions00(self):
        ''' csnContextTests: test read from options v0.0. '''
        # test the options conversion
        self.ReadOptionsTest("options00.txt")

    def testReadOptions10(self):
        ''' csnContextTests: test read from options v1.0. '''
        # test the options conversion
        self.ReadOptionsTest("options10.txt")

    def ValuesTest(self, options):
        self.assertEqual( options.GetAskToLaunchIDE(), True )
        self.assertEqual( options.GetContextFilename(), "E:\\devel\\src\\toolkit\\module_clean.CSnakeGUI" )

    def ReadOptionsTest(self, filename):
        ''' csnContextTests: test read options. '''
        # try to read the file
        options = Options()
        options.Load(filename)
        
        # test values 
        self.ValuesTest(options)
        
        # save it
        newFilename = "new_%s" % filename
        options.Save(newFilename)
        
        # re-read
        newOptions = Options()
        newOptions.Load(newFilename)
        
        # test values 
        self.ValuesTest(newOptions)

        # clean up
        os.remove(newFilename)
       
if __name__ == "__main__":
    unittest.main() 
