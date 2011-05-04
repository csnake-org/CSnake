## @package csnContextTests
# Definition of the csnContextTests class.
# \ingroup tests
import unittest
import os
import csnContext
from csnContext import Context
import shutil

class csnContextTests(unittest.TestCase):
    """ Unit tests for the csnContextConverter methods. """
    
    def testReadContext00(self):
        ''' csnContextTests: test read from context v0.0. '''
        # this version needs the options file
        newFilename = "options"
        shutil.copy("options00a.txt", newFilename)
        # test the context conversion
        self.ReadContextTest(0.0, "context00a.txt")
        # clean up
        os.remove(newFilename)
        
        # this one should throw without the options file
        filename = "context00a.txt"
        self.assertRaises(IOError, self.ReadContextTest, 0.0, filename)
        # clean up
        os.remove("test_%s" % filename)

    def testReadContext10(self):
        ''' csnContextTests: test read from context v1.0. '''
        # this version needs the options file
        newFilename = "options"
        shutil.copy("options00a.txt", newFilename)
        # test the context conversion
        self.ReadContextTest(1.0, "context10a.txt")
        # clean up
        os.remove(newFilename)

        # this one should throw without the options file
        filename = "context10a.txt"
        self.assertRaises(IOError, self.ReadContextTest, 1.0, filename)
        # clean up
        os.remove("test_%s" % filename)

    def testReadContext20(self):
        ''' csnContextTests: test read from context v2.0. '''
        # test the context conversion
        # with field compiler
        self.ReadContextTest(2.0, "context20a.txt")
        # with field compilername
        self.ReadContextTest(2.0, "context20b.txt")
        # with multiple third parties
        self.ReadContextTest(2.0, "context20c.txt")
        
    def testReadContext21(self):
        ''' csnContextTests: test read from context v2.1. '''
        # test the context conversion
        self.ReadContextTest(2.1, "context21a.txt")

    def ValuesTest(self, version, context):
        # [CSnake]
        self.assertEqual( context.GetInstallFolder(), "E:/devel/bin/toolkit/clean/install" )
        self.assertEqual( context.GetFilter(), ["BaseLibVTKTests", "CILabMacrosTests", "RegLibTests"] )
        self.assertEqual( context.GetTestRunnerTemplate(), "normalRunner.tpl" )
        self.assertEqual( context.GetBuildFolder(), "E:/devel/bin/toolkit/clean" )
        self.assertEqual( context.GetCsnakeFile(), "E:/devel/src/toolkit/clean/src/cilabModules/BaseLib/csnBaseLib.py" )
        self.assertEqual( context.GetIdePath(), "D:/Program Files (x86)/Microsoft Visual Studio 9.0/Common7/IDE/devenv.exe" )
        self.assertEqual( context.GetCompilername(), "Visual Studio 9 2008 Win64" )
        self.assertEqual( context.GetPrebuiltBinariesFolder(), "" )                  
        self.assertEqual( context.GetInstance(), "baseLib" )                  
        self.assertEqual( context.GetConfigurationName(), "DebugAndRelease" )                  
        self.assertEqual( context.GetCmakePath(), "C:/Program Files (x86)/CMake 2.8/bin/cmake.exe" )                  
        self.assertEqual( context.GetPythonPath(), "C:/Program Files (x86)/Python 2.6/python.exe" )                  
        self.assertEqual( context.GetKdevelopProjectFolder(), "" )                  
        # [ThirdPartyBuildFolders]
        self.assertEqual( context.GetThirdPartyBuildFolders(), ["E:/devel/bin/toolkit/clean/thirdParty"] )
        # [RootFolders]
        self.assertEqual( context.GetRootFolders(), ["E:/devel/src/toolkit/clean/src"] )
        # [ThirdPartyFolders]
        self.assertEqual( context.GetThirdPartyFolders(), ["E:/devel/src/toolkit/clean/thirdParty"] )

        if version >= 2.0:
            # [RecentlyUsedCSnakeFiles]
            recentContext = Context()
            recentContext.SetInstance("dcmAPI")
            recentContext.SetCsnakeFile("E:/devel/src/toolkit/clean/src/cilabModules/DcmAPI/csnDcmAPI.py")
            recents = context.GetRecentlyUsed()
            self.assertTrue( len(recents), 1 )
            self.assertTrue( recentContext.GetData().Equal(recents[0]) )
    
    def ReadContextTest(self, version, inputFilename):
        ''' csnContextTests: test read context. '''
        # create a copy of the input file
        filename = "test_%s" % inputFilename
        shutil.copy(inputFilename, filename)
        
        # try to read the new one
        context = Context()
        context.Load(filename)

        # test values 
        self.ValuesTest(version, context)
                          
        # save it
        newFilename = "new_%s" % filename
        context.Save(newFilename)
        
        # re-read
        newContext = Context()
        newContext.Load(newFilename)
        
        # test values 
        self.ValuesTest(csnContext.latestFileFormatVersion, newContext)

        # clean up
        os.remove(filename)
        os.remove(newFilename)
        backupFilename = "%s.bk" % filename
        if os.path.isfile(backupFilename):
            os.remove(backupFilename)
       
if __name__ == "__main__":
    unittest.main() 
