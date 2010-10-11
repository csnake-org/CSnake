# Unit tests for the csnContextConverter methods
import unittest
import os
from csnGUIOptions import Options
import shutil

class csnGUIOptionsTests(unittest.TestCase):

    def testReadOptions00(self):
        ''' csnContextTests: test read from options v0.0. '''
        # test the options conversion
        self.ReadOptionsTest("options00a.txt")

    def testReadOptions10(self):
        ''' csnContextTests: test read from options v1.0. '''
        # test the options conversion
        self.ReadOptionsTest("options10a.txt")

    def ValuesTest(self, options):
        self.assertEqual( options.GetAskToLaunchIDE(), True )
        self.assertEqual( options.GetContextFilename(), "E:\\devel\\src\\toolkit\\module_clean.CSnakeGUI" )

    def ReadOptionsTest(self, inputFilename):
        ''' csnContextTests: test read options. '''
        # create a copy of the input file
        filename = "test_%s" % inputFilename
        shutil.copy(inputFilename, filename)
        
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
        os.remove(filename)
        os.remove(newFilename)
        backupFilename = "%s.bk" % filename
        if os.path.isfile(backupFilename):
            os.remove(backupFilename)
       
if __name__ == "__main__":
    unittest.main() 
