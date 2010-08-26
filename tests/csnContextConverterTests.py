# Unit tests for the csnContextConverter methods
import unittest
from csnContextConverter import Converter
from csnGUIOptions import Options
import ConfigParser
import os

class csnContextConverterTests(unittest.TestCase):

    def testConvert(self):
        ''' csnContextConverterTests: test convert. '''
        filename = "test_options"
        contextFilename = "context.txt"
        
        # create an old format option file
        parser = ConfigParser.ConfigParser()
        section = "CSnake"
        parser.add_section(section)
        parser.set(section, "asktolaunchvisualstudio", True)
        parser.set(section, "cmakebuildtype", "DebugAndRelease")
        parser.set(section, "pythonpath", "D:/Python24/python.exe")
        parser.set(section, "visualstudiopath", "")
        parser.set(section, "cmakepath", "CMake")
        parser.set(section, "currentguisettingsfilename", contextFilename)
        parser.set(section, "compiler", "Visual Studio 7 .NET 2003")
        # write the file
        optionFile = open(filename, 'w')
        parser.write(optionFile)
        optionFile.close()
        
        # convert the file
        converter = Converter(filename)
        converter.ConvertOptions()
        
        # try to read the new one
        options = Options()
        options.Load(filename)
        assert options.GetAskToLaunchIDE() == True
        assert options.GetContextFilename() == contextFilename
        
        # clean up
        os.remove(filename)
        os.remove(filename + ".archiveFromVersion")
    
if __name__ == "__main__":
    unittest.main() 
