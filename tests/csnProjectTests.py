# Unit tests for the csnProject class
import unittest
import os
import csnUtility
import csnBuild
import csnProject
import csnGenerator
import csnDependencies
import shutil

class csnProjectTests(unittest.TestCase):
    
    def setUp(self):
        """ Run before test. """

    def tearDown(self):
        """ Run after test. """

    def testName(self):
        """ csnProjectTests: test that the name of the project is correct. """
        # dummyLib project
        dummyLib = csnProject.Project("DummyLib", "library")

        # check the name
        self.assertEqual(dummyLib.name, "DummyLib")

    def testAddSources(self):
        """ csnProjectTests: test that a non-existing source file is detected. """
        # dummyLib project
        dummyLib = csnProject.Project("DummyLib", "library")

        # check adding non existing file
        self.assertRaises(IOError, dummyLib.AddSources, ["main.cpp"])
        
    def testAddProjectsTwice(self):
        """ csnProjectTests: test that adding a project twice has no effect. """
        # dummyLib project
        dummyLib = csnProject.Project("DummyLib", "library")
        # dummyExe project
        dummyExe = csnProject.Project("DummyExe", "executable")
        
        # add dummyLib a first time
        dummyExe.AddProjects([dummyLib])
        # count projects
        nProjects = len(dummyExe.dependenciesManager.projects)
        # add dummyLib another time
        dummyExe.AddProjects([dummyLib])
        # test same number of projects
        self.assertEqual(nProjects, len(dummyExe.dependenciesManager.projects))

    def testAddProjectsNameConflict(self):
        """ csnProjectTests: test that two projects cannot have the same name. """
        # dummyLib project
        dummyLib = csnProject.Project("DummyLib", "library")
        # dummyLib2 project: same name as dummyLib
        dummyLib2 = csnProject.Project("DummyLib", "library")
        # dummyExe project
        dummyExe = csnProject.Project("DummyExe", "executable")

        # add dummyLib
        dummyExe.AddProjects([dummyLib])
        # add dummyLib2
        dummyExe.AddProjects([dummyLib2])
        # get the generator
        generator = csnBuild.Generator()
        # test NameErrot
        self.assertRaises(NameError, generator.Generate, dummyExe)
        # clean up
        shutil.rmtree( csnProject.globalCurrentContext.buildFolder )
        
    def testAddProjectsSelfDependency(self):
        """ csnProjectTests: test that a project cannot depend on itself. """
        # dummyExe project
        dummyExe = csnProject.Project("DummyExe", "executable")
        
        # test adding self
        self.assertRaises(csnDependencies.DependencyError, dummyExe.AddProjects, [dummyExe])
        
    def testAddProjectsCyclicDependency(self):
        """ csnProjectTests: test that a cylic dependency is detected. """
        # dummyLib project
        dummyLib = csnProject.Project("DummyLib", "library")
        # dummyExe project
        dummyExe = csnProject.Project("DummyExe", "executable")
        
        # dummyExe depends on dummyLib
        dummyExe.AddProjects([dummyLib])
        # try making dummyLib depend on dummyExe
        self.assertRaises(csnDependencies.DependencyError, dummyLib.AddProjects, [dummyExe])

    def testBuildBinFolderSlashes(self):
        """ csnProjectTests: test that build bin folder may not contain any backward slashes. """
        # dummyExe project
        dummyExe = csnProject.Project("DummyExe", "executable")

        # get the generator
        generator = csnBuild.Generator()
        # replace the build folder
        testPath = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")
        csnProject.globalCurrentContext.buildFolder = "%s\\%s" % (testPath, "temp_bin")
        # test SyntaxError
        self.assertRaises(csnGenerator.SyntaxError, generator.Generate, dummyExe)

    def testGlob(self):
        """ csnProjectTests: test that globbing source files works. """
        # dummyExe project
        dummyExe = csnProject.Project("DummyExe", "executable")
        dummyExe.AddSources(["src/DummyExe/src/*.cpp"])
        # should have 1 source files
        assert len(dummyExe.GetSources()) == 1, csnUtility.Join(dummyExe.GetSources(), _addQuotes=1)

    def testSourceRootFolder(self):
        """ csnProjectTests: test that the source root folder, containing csnBuildTest.py, is deduced correctly by the parent class csnBuild.Project. """
        # dummyExe project
        dummyExe = csnProject.Project("DummyExe", "executable")
        dummyExe.AddSources(["src/DummyExe/src/*.cpp"])
        
        # check folder
        self.assertEqual(os.path.abspath(dummyExe.sourceRootFolder), os.path.abspath(os.path.dirname(__file__)))
    
if __name__ == "__main__":
    unittest.main() 