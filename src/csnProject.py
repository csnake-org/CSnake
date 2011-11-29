## @package csnProject
# Definition of the Project handling related classes. 
import csnUtility
import csnDependencies
import csnProjectPaths
import csnInstall
import csnCompile
import csnTests
import inspect
import os.path
import types
import new
from csnUtility import MakeValidIdentifier
import re

globalCurrentContext = None

def FindFilename(level = 0):
    """
    level - 0: Find filename of the script calling FindFilename (default),
            1: Find filename of the script calling the function that calls FindFilename,
            x: Find filename of the script calling FindFilename indirectly through x+1 function calls
    """
    frame = inspect.currentframe(1+level)
    try:
        if frame is None:
            # inspect.currentframe is not available with all python interpreters, so use inspect.stack as fallback option
            filename = inspect.stack()[1+level][1]
        else:
            filename = inspect.getframeinfo(frame)[0]
    finally:
        # make sure the reference to the frame is deleted in any case (avoid cycles, see http://docs.python.org/library/inspect.html#the-interpreter-stack)
        del frame
    return filename

def Project(_name, _type, _sourceRootFolder = None, _categories = None):
    if _sourceRootFolder is None:
        _sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(FindFilename(1)))
    return globalCurrentContext.CreateProject(_name, _type, _sourceRootFolder, _categories)

def Dll(_name, _sourceRootFolder = None, _categories = None):
    if _sourceRootFolder is None:
        _sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(FindFilename(1)))
    return Project(_name, "dll", _sourceRootFolder, _categories)

def Library(_name, _sourceRootFolder = None, _categories = None):
    if _sourceRootFolder is None:
        _sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(FindFilename(1)))
    return Project(_name, "library", _sourceRootFolder, _categories)

def Executable(_name, _sourceRootFolder = None, _categories = None):
    if _sourceRootFolder is None:
        _sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(FindFilename(1)))
    return Project(_name, "executable", _sourceRootFolder, _categories)

def LoadThirdPartyModule(_subFolder, _name):
    """ Loads third party module _name from subfolder _subFolder of the third party folder """
    global globalCurrentContext
    folderList = []
    for thirdPartyFolder in globalCurrentContext.GetThirdPartyFolders( ):
        folderList.append( "%s/%s" % (thirdPartyFolder, _subFolder) )
    return csnUtility.LoadModules(folderList, _name)

class Rule:
    """ This class contains a build rule for e.g. Visual Studio, Make, etc """
    def __init__(self):
        self.workingDirectory = ""
        self.command = ""
        self.output = ""
        self.depends = ""

def ToProject(project):
    """
    Helper function that tests if its argument (project) is a function. If so, it returns the result of the function. 
    If not, it returns its argument (project). It is used to treat Project instances and functions returning a Project instance
    in the same way.
    """
    if type(project) == types.FunctionType:
        project = project()
    if hasattr(project, "_APIVeryGenericProject_Base__project"):
        project = project._APIVeryGenericProject_Base__project
    return project

# Going to be renamed to "GenericProject" in 3.0
class VeryGenericProject(object):
    """ Very very generic project... """
    def __init__(self, name, type, sourceRootFolder = None, categories = None, context = None):
        # name
        self.name = name
        # type: dll, exe, tp
        self.type = type
        # source root folder
        if sourceRootFolder is None:
            sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(FindFilename(1)))
        # categories: ~name
        self.categories = categories
        if self.categories is None:
            self.categories = []
        # context
        self.context = context

        # managers
        self.pathsManager = csnProjectPaths.Manager(self, sourceRootFolder)
        self.dependenciesManager = csnDependencies.Manager(self)
        self.installManager = csnInstall.Manager(self)

    def GetSourceRootFolder(self):
        return self.pathsManager.GetSourceRootFolder()

    # sourceRootFolder property
    sourceRootFolder = property(GetSourceRootFolder)

    def AddProjects(self, _projects, _dependency = True, _includeInSolution = True): 
        """ Add dependencies to the project. """
        self.dependenciesManager.AddProjects(_projects, _dependency, _includeInSolution)

    def GetProjects(self, _recursive = False, 
            _onlyRequiredProjects = False, 
            _includeSelf = False, 
            _onlyPublicDependencies = False,
            _onlyNonRequiredProjects = False, 
            _filter = True):
        """ Get the dependencies of this project in a sorted array (dependencies before dependents). """
        return self.dependenciesManager.GetProjects(_recursive, 
            _onlyRequiredProjects, 
            _includeSelf, 
            _onlyPublicDependencies,
            _onlyNonRequiredProjects, 
            _filter)
        
    def AddFilesToInstall(self, _list, _location = None, 
              _debugOnly = 0, _releaseOnly = 0, 
              _WIN32 = 0, _NOT_WIN32 = 0):
        """ Add files to copy (install) to the build folder. """
        self.installManager.AddFilesToInstall(_list, _location, 
              _debugOnly, _releaseOnly, 
              _WIN32, _NOT_WIN32)
        
    def GetBuildFolder(self):
        """ Get the build folder. """
        assert False, "To be implemented in subclass." 
                
    def MatchesFilter(self):
        for pattern in self.context.GetFilter():
            for string in self.categories:
                if csnUtility.Matches(string, pattern):
                    return True
        return False

    def Glob(self, _path):
        return self.pathsManager.Glob(_path)
    
# Going to be renamed to "CompiledProject" in 3.0
class GenericProject(VeryGenericProject):
    """
    The constructors initialises these member variables:
    self.buildSubFolder -- Direct subfolder - within the build folder - for this project. Is either 'executable' or 'library'.
    self.installSubfolder -- Direct subfolder - within the install folder - for targets generated by this project.
    self.useBefore -- A list of projects. The use-file of this project must be included before the use-file of the projects in this list.
    self.configFilePath -- Path to the config file for the project.
    self.sources -- Sources to be compiled for this target.
    self.sourceGroups -- Dictionary (groupName -> sources) for sources that should be placed in a visual studio group.
    self.rules - CMake rules. See AddRule function.
    self.sourcesToBeMoced -- Sources for which a qt moc file must be generated.
    self.sourcesToBeUIed -- Sources for which qt's UI.exe must be run.
    self.filesToInstall -- Contains files to be installed in the build results folder. It has the structure filesToInstall[mode][installPath] = files.
    For example: if self.filesToInstall[\"Debug\"][\"data\"] = [\"c:/one.txt\", \"c:/two.txt\"], 
    then c:/one.txt and c:/two.txt must be installed in the data subfolder of the install folder when in debug mode.
    self.projects -- Set of related project instances. These projects have been added to self using AddProjects.
    self.projectsNonRequired -- Subset of self.projects. Contains projects that self doesn't depend on.
    The project does not add a dependency on any project in this list.      
    self.generateWin32Header -- Flag that says if a standard Win32Header.h must be generated
    self.precompiledHeader -- Name of the precompiled header file. If non-empty, and using Visual Studio (on Windows),
    then precompiled headers are used for this project.
    self.customCommands -- List of extra commands that must be run when configuring this project.
    self.properties -- Custom properties for the target that will use the command ADD_PROPERTY( TARGET PROPERTY <name> [value1 ... )
    """
    
    def __init__(self, _name, _type, _sourceRootFolder = None, _categories = None, _context = None):
        """
        _type -- Type of the project, should be \"executable\", \"library\", \"dll\" or \"third party\".
        _name -- Name of the project, e.g. \"SampleApp\".
        _sourceRootFolder -- Folder used for locating source files for this project. If None, then the folder name is derived from 
        the call stack. For example, if this class' constructor is called in a file d:/users/me/csnMyProject.py, then d:/users/me 
        will be set as the source root folder.
        """    
        if _sourceRootFolder is None:
            _sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(FindFilename(1)))
        VeryGenericProject.__init__(self, _name, _type, _sourceRootFolder, _categories, _context)

        # Get the thirdPartyBuildFolder index
        # WARNING: this is only valid for a thirdparty projects!!!
        self.thirdPartyIndex = 0
        count = 0
        for folder in self.context.GetThirdPartyFolders():
            if folder == os.path.dirname(_sourceRootFolder):
                self.thirdPartyIndex = count
                break
            count += 1
        
        self.rules = dict()
        self.customCommands = []
        self.__compileManager = csnCompile.Manager(self)
        self.__compileManagerUpdates = list()
        self.installSubFolder = ""
        self.testsManager = csnTests.Manager(self)
        self.properties = []
        self.__postCMakeTasks = []
        self.listCmakeInsertBeforeTarget = list()
        self.listCmakeInsertAfterTarget = list()
        self.listCmakeInsertBeginning = list()
        
        for flag in globalCurrentContext.GetCompiler().GetCompileFlags():
            self.__compileManager.private.definitions.append(flag)
        
        # Function called before "ADD_LIBARRY"
        self.CMakeInsertBeforeTarget = new.instancemethod(SetCMakeInsertBeforeTarget, self)
        # Function called after "ADD_LIBARRY"
        self.CMakeInsertAfterTarget = new.instancemethod(SetCMakeInsertAfterTarget, self)
        # Function called at the beginning of the CMakeList
        self.CMakeInsertBeginning = new.instancemethod(SetCMakeInsertBeginning, self)
        

    def AddSources(self, _listOfSourceFiles, _moc = 0, _ui = 0, _sourceGroup = "", _checkExists = 1, _forceAdd = 0):
        self.__compileManagerUpdates.append((self.__compileManager.AddSources, {
            "_listOfSourceFiles" : _listOfSourceFiles,
            "_moc"               : _moc,
            "_ui"                : _ui,
            "_sourceGroup"       : _sourceGroup,
            "_checkExists"       : _checkExists,
            "_forceAdd"          : _forceAdd
          }))
                   
    def RemoveSources(self, _listOfSourceFiles):
        self.__compileManagerUpdates.append((self.__compileManager.RemoveSources, {
            "_listOfSourceFiles" : _listOfSourceFiles
          }))
                            
    def AddDefinitions(self, _listOfDefinitions, _private = 0, _WIN32 = 0, _NOT_WIN32 = 0 ):
        self.__compileManagerUpdates.append((self.__compileManager.AddDefinitions, {
            "_listOfDefinitions" : _listOfDefinitions,
            "_private"           : _private,
            "_WIN32"             : _WIN32,
            "_NOT_WIN32"         : _NOT_WIN32
          }))
        
    def AddIncludeFolders(self, _listOfIncludeFolders, _WIN32 = 0, _NOT_WIN32 = 0):
        self.__compileManagerUpdates.append((self.__compileManager.AddIncludeFolders, {
            "_listOfIncludeFolders" : _listOfIncludeFolders,
            "_WIN32"                : _WIN32,
            "_NOT_WIN32"            : _NOT_WIN32
          }))
        
    def SetPrecompiledHeader(self, _precompiledHeader):
        self.__compileManagerUpdates.append((self.__compileManager.SetPrecompiledHeader, {
            "_precompiledHeader" : _precompiledHeader
          }))
        
    def AddLibraryFolders(self, _listOfLibraryFolders, _WIN32 = 0, _NOT_WIN32 = 0):
        self.__compileManagerUpdates.append((self.__compileManager.AddLibraryFolders, {
            "_listOfLibraryFolders" : _listOfLibraryFolders,
            "_WIN32"                : _WIN32,
            "_NOT_WIN32"            : _NOT_WIN32
          }))
        
    def AddLibraries(self, _listOfLibraries, _WIN32 = 0, _NOT_WIN32 = 0, _debugOnly = 0, _releaseOnly = 0):
        self.__compileManagerUpdates.append((self.__compileManager.AddLibraries, {
            "_listOfLibraries" : _listOfLibraries,
            "_WIN32"           : _WIN32,
            "_NOT_WIN32"       : _NOT_WIN32,
            "_debugOnly"       : _debugOnly,
            "_releaseOnly"     : _releaseOnly
          }))
        
    def UseBefore(self, _otherProject):
        """ Was useful when projects were not sorted, not anymore... """
        self.dependenciesManager.UseBefore(_otherProject)

    def AddRule(self, description, output, command, depends, workingDirectory = "."):
        """
        Adds a new rule to the self.rules dictionary, using description as the key.
        """
        rule = Rule()
        rule.output = output
        rule.command = command
        rule.depends = depends
        rule.workingDirectory = workingDirectory
        self.rules[description] = rule

    def AddCustomCommand(self, _command):
        self.customCommands.append(_command)

    def RunCustomCommands(self):
        for command in self.customCommands:
            command(self)
            
    def AddTests(self, _listOfTests, _cxxTestProject, _enableWxWidgets = 0, _dependencies = None, _pch = ""):
        self.testsManager.AddTests(_listOfTests, _cxxTestProject, _enableWxWidgets, _dependencies, _pch)
    
    def SetGenerateWin32Header(self, _setHeader):
        self.__compileManager.generateWin32Header = _setHeader

    def GetTestProject(self):
        return self.testsManager.testProject
        
    def GetBuildFolder(self):
        if self.type == "third party":
            return self.context.GetThirdPartyBuildFolderByIndex(self.thirdPartyIndex)
        else:
            return self.pathsManager.GetBuildFolder()

    def GetBuildResultsFolder(self, _configurationName = "${CMAKE_CFG_INTDIR}"):
        return self.pathsManager.GetBuildResultsFolder(_configurationName)

    def GetCMakeListsFilename(self):
        return "%s/%s" % (self.context.GetBuildFolder(), self.pathsManager.cmakeListsSubpath)

    def GetCompileManager(self):
        if len(self.__compileManagerUpdates) > 0:
            for function, parameters in self.__compileManagerUpdates:
                function(**parameters)
            self.__compileManagerUpdates = list()
            if( len(self.__compileManager.sources) == 0 ):
                dummySource = csnUtility.GetDummyCppFilename()
                self.__compileManager.AddSources([dummySource])
        return self.__compileManager

    def GetSources(self):
        return self.GetCompileManager().sources
        
    testProject = property(GetTestProject)

    def Dump(self):
        dump = dict()
        for project in self.dependenciesManager.GetProjects(_recursive=True, _includeSelf=True):
            dump[project.name] = {
                #"compiler" : project.__compileManager.Dump()
                #"dependencies" : project.dependenciesManager.Dump(), \
                #"install" : project.installManager.Dump(), \
                #"paths" : project.pathsManager.Dump() \
            }
        return dump

    def AddProperties(self, _property):
        for property in _property:
            self.properties.append(property)

    def GetPostCMakeTasks(self):
        return self.__postCMakeTasks
    
    def AddPostCMakeTasks(self, tasks):
        for task in tasks:
            self.__postCMakeTasks.append(task)
            
    def CreateHeader(self, _filename = None, _variables = None, _variablePrefix = None):
        """ 
        Creates a header file with input vars for the given project.
    
        @param _filename The header file name (will be created in the projects' build folder), defaults to project name
        @param _variables Dictionary of variable/value pairs
        @param _variablesPrefix Prefix for the names of the variables in parameter _variables, defaults to project name
        """
        self.header = (_filename, _variables, _variablePrefix)
        self.AddCustomCommand(self.CreateHeaderDo)
    
    def CreateHeaderDo(self, ignoredProject):
        (filename, variables, variablePrefix) = self.header
        projectNameClean = re.sub(r"[^A-Za-z0-9]", "_", self.name)
        if not filename: 
            filename = "%s.h" % projectNameClean
        path = "%s/%s" % (self.GetBuildFolder(), filename)
        
        # TODO: Only create the header, if it either doesn't exist or source has changed
        # TODO: Create directory, if it doesn't exist
        headerFile = open(path, 'w')
        
        # header
        guard = MakeValidIdentifier(_identifier = filename, _toUpper = True)
        headerFile.write("#ifndef %s\n" % guard)
        headerFile.write("#define %s\n" % guard)
        headerFile.write("\n")
        headerFile.write("// Automatically generated file, do not edit.\n")
        headerFile.write("\n")
        
        # default variables
        if not variablePrefix:
            variablePrefix = MakeValidIdentifier(_identifier = self.name, _toUpper = True)
        headerFile.write("#define %s_FOLDER \"%s/..\"\n" % (variablePrefix, self.GetSourceRootFolder()))
        headerFile.write("#define %s_BUILD_FOLDER \"%s\"\n" % (variablePrefix, self.GetBuildFolder()))
        
        # input variables
        if variables:
            headerFile.write("\n")
            for (key, value) in variables:
                headerFile.write("#define %s \"%s\"\n" % (key, value))
        
        headerFile.write("\n")
        headerFile.write("#endif // %s\n" % guard)
        headerFile.close()
    
    def AddCMakeInsertBeforeTarget(self, callback, wrappedProject, parameters = {}):
        self.listCmakeInsertBeforeTarget.append((callback, wrappedProject, parameters))
    
    def AddCMakeInsertAfterTarget(self, callback, wrappedProject, parameters = {}):
        self.listCmakeInsertAfterTarget.append((callback, wrappedProject, parameters))
    
    def AddCMakeInsertBeginning(self, callback, wrappedProject, parameters = {}):
        self.listCmakeInsertBeginning.append((callback, wrappedProject, parameters))


def SetCMakeInsertBeforeTarget(self, _file):
    for (callback, wrappedProject, parameters) in self.listCmakeInsertBeforeTarget:
        result = callback(wrappedProject, **parameters)
        if isinstance(result, str) or isinstance(result, unicode):
            _file.write("\n# Start code from callback function '%s'\n" % callback.__name__)
            _file.write(result)
            _file.write("\n# End code from callback function '%s'\n\n" % callback.__name__)
    return

def SetCMakeInsertAfterTarget(self, _file):
    for (callback, wrappedProject, parameters) in self.listCmakeInsertAfterTarget:
        result = callback(wrappedProject, **parameters)
        if isinstance(result, str) or isinstance(result, unicode):
            _file.write("\n# Start code from callback function '%s'\n" % callback.__name__)
            _file.write(result)
            _file.write("\n# End code from callback function '%s'\n\n" % callback.__name__)
    return

def SetCMakeInsertBeginning(self, _file):
    for (callback, wrappedProject, parameters) in self.listCmakeInsertBeginning:
        result = callback(wrappedProject, **parameters)
        if isinstance(result, str) or isinstance(result, unicode):
            _file.write("\n# Start code from callback function '%s'\n" % callback.__name__)
            _file.write(result)
            _file.write("\n# End code from callback function '%s'\n\n" % callback.__name__)
    return

class ThirdPartyProject(VeryGenericProject):
    """ Third Party project. """
    def __init__(self, name, context, sourceRootFolder=None):
        if sourceRootFolder is None:
            sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(FindFilename(1)))
        VeryGenericProject.__init__(self, name, "third party", sourceRootFolder, None, context)

        # Get the thirdPartyBuildFolder index
        # WARNING: this is only valid for a thirdparty projects!!!
        self.thirdPartyIndex = 0
        count = 0
        for folder in self.context.GetThirdPartyFolders():
            if folder == os.path.dirname(sourceRootFolder):
                self.thirdPartyIndex = count
                break
            count += 1
        
    def GetBuildFolder(self):
        return self.context.GetThirdPartyBuildFolderByIndex(self.thirdPartyIndex)
    
    def SetUseFilePath(self, path):
        """ Set the path of the cmake *use* file. """
        self.pathsManager.useFilePath = path

    def SetConfigFilePath(self, path):
        """ Set the path of the cmake *config* file. """
        self.pathsManager.configFilePath = path
