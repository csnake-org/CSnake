import os
import csnUtility
import csnProject

class Manager:
    def __init__(self, _project):
        self.holdingProject = _project
        self.testRunnerSourceFile = None
        self.testProject = None
    
    def __CreateTestProject(self, _cxxTestProject, _enableWxWidgets = 0):
        """
        Creates a test project in self.testProject. This testProject will be configured by CMake, and will run the tests for this
        project (i.e. for self).
        _cxxTestProject - May be the cxxTest project instance, or a function returning a cxxTest project instance.
        _enableWxWidgets - If true, the CMake rule that creates the testrunner will create a test runner that initializes wxWidgets, so that
        your tests can create wxWidgets objects.
        """
        testsName = "%sTests" % self.holdingProject.name
        self.testProject = self.holdingProject.context.CreateProject(
            "%sTests" % self.holdingProject.name, "executable", 
            _sourceRootFolder = self.holdingProject.GetSourceRootFolder(), 
            _categories = [testsName]
        )
        self.holdingProject.context.SetSuperSubCategory("Tests", testsName)
        self.testProject.AddDefinitions(["/DCXXTEST_HAVE_EH"], _private = 1, _WIN32 = 1)
        self.testProject.AddDefinitions(["-DCXXTEST_HAVE_EH"], _private = 1, _NOT_WIN32 = 1)
        
        self.testProject.AddProjects([_cxxTestProject, self.holdingProject])
        self.holdingProject.AddProjects([self.testProject], _dependency = False)
        
        self.testRunnerSourceFile = "%s/%s.cpp" % (self.testProject.GetBuildFolder(), self.testProject.name)
        if not os.path.exists(self.testRunnerSourceFile):
            if not os.path.exists(self.testProject.GetBuildFolder()):
                os.makedirs(self.testProject.GetBuildFolder())
            f = open(self.testRunnerSourceFile, 'w')
            f.write("// Test runner source file. To be created by CxxTest.py.")
            f.close()
            
        self.testProject.AddSources([self.testRunnerSourceFile], _checkExists = 0, _forceAdd = 1)
        
    def AddTests(self, listOfTests, _cxxTestProject, _enableWxWidgets = 0, _dependencies = None):
        """
        _cxxTestProject -- May be the cxxTest project instance, or a function returning a cxxTest project instance.
        listOfTests -- List of source files containing cxx test classes.
        """
        cxxTestProject = csnProject.ToProject(_cxxTestProject)
        
        if self.testProject is None:
            self.__CreateTestProject(cxxTestProject, _enableWxWidgets)
            
        for test in listOfTests:
            absPathToTest = self.testProject.pathsManager.PrependRootFolderToRelativePath(test)
            self.testProject.AddSources([absPathToTest], _checkExists = 0)

        wxRunnerArg = None
        if _enableWxWidgets:
            wxRunnerArg = "--template \"%s\"" % (csnUtility.GetRootOfCSnake() + "/resources/wxRunner.tpl")
        else:
            wxRunnerArg = "--template \"%s\"" % (csnUtility.GetRootOfCSnake() + "/resources/%s" % self.testProject.context.testRunnerTemplate)    
            
        pythonScript = "%s/CxxTest/cxxtestgen.py" % cxxTestProject.GetSourceRootFolder()
        command = "\"%s\" \"%s\" %s --have-eh --error-printer -o \"%s\" " % (
            csnUtility.NormalizePath(self.testProject.context.pythonPath), 
            pythonScript, 
            wxRunnerArg, 
            self.testRunnerSourceFile
        )
        for source in self.testProject.GetSources():
            if os.path.splitext(source)[1] in (".h", ".hpp"):
                command += "\"%s\"" % source
        self.testProject.AddRule("Create test runner", self.testRunnerSourceFile, command)
        
        if not _dependencies is None:
            self.testProject.AddProjects(_dependencies)
