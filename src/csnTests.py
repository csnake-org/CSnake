import os
import csnUtility
import csnProject
import new

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
        self.testProject.AddSources([self.testRunnerSourceFile], _checkExists = 0, _forceAdd = 1)
        
    def AddTests(self, listOfTests, _cxxTestProject, _enableWxWidgets = 0, _dependencies = None, _pch = ""):
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
            wxRunnerArg = "--template \"%s\"" % (csnUtility.GetRootOfCSnake() + "/resources/%s" % self.testProject.context.GetTestRunnerTemplate())    
            
        pythonScript = "%s/CxxTest/cxxtestgen.py" % cxxTestProject.GetSourceRootFolder()
        command = "\"%s\" \"%s\" %s --have-eh --error-printer -o \"%s\" " % (
            csnUtility.NormalizePath(self.testProject.context.GetPythonPath()), 
            pythonScript, 
            wxRunnerArg, 
            self.testRunnerSourceFile
        )
        depends = []
        for source in self.testProject.GetSources():
            if os.path.splitext(source)[1] in (".h", ".hpp"):
                depends.append( '"%s"' % source )
                command += ' "%s"' % source
        self.testProject.AddRule("Create test runner", self.testRunnerSourceFile, command, depends)
        self.testProject.AddCMakeInsertAfterTarget(CustomCMakeLinesTest, self.testProject)
        self.holdingProject.AddCMakeInsertBeginning(CustomCMakeLinesTestHoldingProject, self.holdingProject)
        self.testProject.AddLibraries(["DelayImp"], _WIN32 = 1)
        
        if not _dependencies is None:
            self.testProject.AddProjects(_dependencies)

        if( _pch != "" ):
            self.testProject.SetPrecompiledHeader(_pch)



def CustomCMakeLinesTest(project):
    """ Line to add tests. """
    cmakecode = ""
    if len( project.GetSources() ) > 0:
        cmakecode += "\n# Adding CMake Test\n"
        cmakecode += "ADD_TEST( ${PROJECT_NAME} ${EXECUTABLE_OUTPUT_PATH}/%s )\n" % project.name
        
        if project.context.GetCompiler().IsForPlatform(_WIN32 = 1, _NOT_WIN32 = 0):
            # Add delay load
            requiredProjects = project.GetProjects( _recursive = True )
            # For each project -> Check the dependent categories
            for project in requiredProjects:
                if project.type == "dll":
                    cmakecode += "SET_TARGET_PROPERTIES( ${PROJECT_NAME} PROPERTIES LINK_FLAGS \"/DELAYLOAD:%s.dll\" )\n" % project.name
    return cmakecode

def CustomCMakeLinesTestHoldingProject(project):
    """ Line to enable testing. """
    return "\n# Enable CMake Testing\nENABLE_TESTING()\n"

