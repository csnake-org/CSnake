import csnUtility
import csnPostProcessorForVisualStudio
import csnPostProcessorForKDevelop
import inspect
import os.path
import warnings
import sys
import re
import glob
import types
import shutil
import OrderedSet

def IsRunningOnWindows():
    """ Returns true if the python script is not running on Windows """
    return sys.platform == "win32"

# ToDo:
# - check that of all root folders, only one contains csnCISTIBToolkit
# - Have public and private related projects (hide the include paths from its clients)
# - If ITK doesn't implement the DONT_INHERIT keyword, then use environment variables to work around the cmake propagation behaviour
# - csn python modules can contain option widgets that are loaded into CSnakeGUI! Use this to add selection of desired toolkit modules in csnGIMIAS
# - Fix module reloading
# - Fix install rules when installing a folder
# - Better GUI: recently used Source Root Folder and associated recently used csnake files.
# - Better GUI: do more checks, give nice error messages
# - If copy_tree copies nothing, check that the source folder is empty
# - On linux, prevent building with all, force use of either debug or release
# - On linux, also create a Debug and Release folder (not happening now, because the cmake type is "")
# - On linux, don't copy any windows dlls
# End: ToDo.

# create variable that contains the folder where csnake is located. The use of /../CSnake ensures that 
# the root folder is set correctly both when running the python interpreter, or when using the binary
# CSnakeGUI executable.
sys.path.append(csnUtility.GetRootOfCSnake())

pythonPath = "D:/Python24/python.exe"

class DependencyError(StandardError):
    pass
    
class SyntaxError(StandardError):
    pass

class ProjectClosedError(StandardError):
    pass

class Rule:
    def __init__(self):
        self.workingDirectory = ""
        self.command = ""

def ToProject(project):
    """
    Helper function that tests if project is a function. If so, it returns the result of the function. If not, it returns project.
    """
    result = project
    if type(project) == types.FunctionType:
        result = project()
    return result

class CompileAndLinkSettings:
    """ 
    Helper class for CompileAndLinkConfig 
    """
    def __init__(self):
        self.definitions = list()
        self.libraries = list()
        self.includeFolders = list()
        self.libraryFolders = list()
        
class CompileAndLinkConfig:
    """ 
    Helper class that contains the settings on an operating system 
    """
    def __init__(self):
        self.public = CompileAndLinkSettings()
        self.private = CompileAndLinkSettings()

class ConfigTypes:
    def __init__(self):
        self.all = "ALL"
        self.win32 = "WIN32"
        self.notWin32 = "NOT WIN32"

    def List(self):
        return [self.all, self.win32, self.notWin32]
        
    def GetOpSysName(self, _WIN32, _NOT_WIN32):
        """
        Returns a type from self.List()
        """
        if( _WIN32 and _NOT_WIN32 ):
            _WIN32 = _NOT_WIN32 = 0
        compiler = self.all
        if( _WIN32 ):
            compiler = self.win32
        elif( _NOT_WIN32 ):
            compiler = self.notWin32
        return compiler
                    
class Generator:
    """
    Generates the CMakeLists.txt for a csnBuild.Project.
    """

    def Generate(self, _targetProject, _binaryFolderForCSnake, _binaryFolderForTheCompiler, _installFolder = "", _cmakeBuildType = "None", _generatedList = None, _knownProjectNames = None):
        """
        Generates the CMakeLists.txt for a csnBuild.Project in _binaryFolderForCSnake.
        When the project is built by the compiler, all binaries will be placed in _binaryFolderForTheCompiler.
        _generatedList -- List of projects for which Generate was already called
        """

        isTopLevelProject = _generatedList is None
        if( _generatedList is None ):
            _generatedList = []
            _knownProjectNames = []

        if( _targetProject.name in _knownProjectNames):
            raise NameError, "Each project must have a unique name. Violating project is %s in folder %s\n" % (_targetProject.name, _targetProject.sourceRootFolder)
        else:
            _knownProjectNames.append(_targetProject.name)
            
        # trying to Generate a project twice indicates a logical error in the code        
        assert not _targetProject in _generatedList, "Target project name = %s" % (_targetProject.name)
        _generatedList.append(_targetProject)
        
        # check for backward slashes
        if csnUtility.HasBackSlash(_binaryFolderForCSnake):
            raise SyntaxError, "Error, backslash found in binary folder %s" % _binaryFolderForCSnake
        if csnUtility.HasBackSlash(_binaryFolderForTheCompiler):
            raise SyntaxError, "Error, backslash found in binary folder %s" % _binaryFolderForTheCompiler
        
        if( _targetProject.type == "third party" ):
            warnings.warn( "CSnake warning: you are trying to generate CMake scripts for a third party module (nothing generated)\n" )
            return
         
        # create binary project folder
        targetProjectBinFolderForCSnake = _targetProject.AbsoluteBinaryFolder(_binaryFolderForCSnake)
        os.path.exists(targetProjectBinFolderForCSnake) or os.makedirs(targetProjectBinFolderForCSnake)
    
        configTypes = ConfigTypes()
        
        # create Win32Header
        if( _targetProject.type != "executable" and _targetProject.GetGenerateWin32Header() ):
            self.__GenerateWin32Header(_targetProject, _binaryFolderForCSnake)
            # add search path to the generated win32 header
            if not targetProjectBinFolderForCSnake in _targetProject.compileAndLinkConfigFor[configTypes.all].public.includeFolders:
                _targetProject.compileAndLinkConfigFor[configTypes.all].public.includeFolders.append(targetProjectBinFolderForCSnake)
        
        # open cmakelists.txt
        fileCMakeLists = "%s/%s" % (_binaryFolderForCSnake, _targetProject.cmakeListsSubpath)
        f = open(fileCMakeLists, 'w')
        
        # write header and some cmake fields
        f.write( "# CMakeLists.txt generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "PROJECT(%s)\n" % (_targetProject.name) )
        f.write( "SET( BINARY_DIR \"%s\")\n" % (_binaryFolderForCSnake) )

        if not _cmakeBuildType == "None":
            f.write( "SET( CMAKE_BUILD_TYPE %s )\n" % (_cmakeBuildType) )
        
        targetProjectInstallSubfolder = "%s/%s" % (_binaryFolderForTheCompiler, _targetProject.installSubFolder)
        
        f.write( "\n# All binary outputs are written to the same folder.\n" )
        f.write( "SET( CMAKE_SUPPRESS_REGENERATION TRUE )\n" )
        f.write( "SET( EXECUTABLE_OUTPUT_PATH \"%s\")\n" % (targetProjectInstallSubfolder) )
        f.write( "SET( LIBRARY_OUTPUT_PATH \"%s\")\n" % (targetProjectInstallSubfolder) )
    
        # create config and use files, and include them
        _targetProject.GenerateConfigFile( _binaryFolderForCSnake, _public = 0)
        _targetProject.GenerateConfigFile( _binaryFolderForCSnake, _public = 1)
        _targetProject.GenerateUseFile(_binaryFolderForCSnake)
        
        _targetProject.CreateCMakeSections(f, _binaryFolderForCSnake, _installFolder)
        _targetProject.CreateExtraSourceFilesForTesting(_binaryFolderForCSnake)

        # Find projects that must be generated. A separate list is used to ease debugging.
        projectsToGenerate = OrderedSet.OrderedSet()
        requiredProjects = _targetProject.RequiredProjects(_recursive = 1)        
        for projectToGenerate in requiredProjects:
            # determine if we must Generate the project. If a required project will generate it, 
            # then leave it to the required project. This will prevent multiple generation of the same project.
            # If a non-required project will generate it, then still generate the project 
            # (the non-required project may depend on target project to generate project, creating a race condition).
            generateProject = not projectToGenerate in _generatedList and projectToGenerate.type != "third party"
            if( generateProject ):
                for requiredProject in _targetProject.RequiredProjects(_recursive = 0):
                    if( requiredProject.DependsOn(projectToGenerate) ):
                        generateProject = 0
            if( generateProject ):
                projectsToGenerate.add(projectToGenerate)
        f.write( "\n" )
        
        # add non-required projects that have not yet been generated to projectsToGenerate
        for project in _targetProject.projectsNonRequired:
            if( not project in _generatedList ):
                projectsToGenerate.add(project)

        # generate projects, and add a line with ADD_SUBDIRECTORY
        for project in projectsToGenerate:
            # check again if a previous iteration of this loop didn't add project to the generated list
            if not project in _generatedList:
                f.write( "ADD_SUBDIRECTORY(\"${BINARY_DIR}/%s\" \"${BINARY_DIR}/%s\")\n" % (project.binarySubfolder, project.binarySubfolder) )
                self.Generate(project, _binaryFolderForCSnake, _binaryFolderForTheCompiler, _installFolder, _cmakeBuildType, _generatedList, _knownProjectNames)
           
        # add dependencies
        f.write( "\n" )
        for project in requiredProjects:
            staticLibUsingAnotherLib = _targetProject.type == "library" and project.type != "executable" 
            noSources = len(project.sources) == 0 
            if (IsRunningOnWindows() and staticLibUsingAnotherLib) or noSources: 
                continue
            else:
                f.write( "ADD_DEPENDENCIES(%s %s)\n" % (_targetProject.name, project.name) )

        # if top level project, add install rules for all the filesToInstall
        if False and isTopLevelProject:
            for mode in ("debug", "release"):
                for project in _targetProject.ProjectsToUse():
                    # iterate over filesToInstall to be copied in this mode
                    for location in project.filesToInstall[mode].keys():
                        files = ""
                        for file in project.filesToInstall[mode][location]:
                            files += "%s " % csnUtility.ForwardSlashes(file)
                        if files != "":
                            destination = "%s/%s" % (_installFolder, location)
                            f.write( "\n# Rule for installing files in location %s\n" % destination)
                            f.write("INSTALL(FILES %s DESTINATION %s CONFIGURATIONS %s)\n" % (files, destination, mode.upper()))
                        
        f.close()

    def PostProcess(self, _targetProject, _binaryFolderForCSnake, _kdevelopProjectFolder = ""):
        """
        Apply post-processing after the CMake generation for _targetProject and all its child projects.
        _binaryFolderForCSnake - The binary folder that was passed to the Generate member function.
        _kdevelopProjectFolder - If generating a KDevelop project, then the KDevelop project file will be
        copied from the bin folder to this folder. This is work around for a problem in 
        KDevelop: it does not show the source tree if the kdevelop project file is in the bin folder.
        """
        projects = OrderedSet.OrderedSet()
        projects.add(_targetProject)
        projects.update( _targetProject.AllProjects(_recursive = 1) )
        ppVisualStudio = csnPostProcessorForVisualStudio.PostProcessor()
        ppKDevelop = csnPostProcessorForKDevelop.PostProcessor()
        for project in projects:
            ppVisualStudio.Do(project, _binaryFolderForCSnake)
        ppKDevelop.Do(_targetProject, _binaryFolderForCSnake, _kdevelopProjectFolder)
    
    def __GenerateWin32Header(self, _targetProject, _binaryFolderForCSnake):
        """
        Generates the ProjectNameWin32.h header file for exporting/importing dll functions.
        """
        templateFilename = csnUtility.GetRootOfCSnake() + "/TemplateSourceFiles/Win32Header.h"
        if( _targetProject.type == "library" ):
            templateFilename = csnUtility.GetRootOfCSnake() + "/TemplateSourceFiles/Win32Header.lib.h"
        templateOutputFilename = "%s/%sWin32Header.h" % (_targetProject.AbsoluteBinaryFolder(_binaryFolderForCSnake), _targetProject.name)
        
        assert os.path.exists(templateFilename), "File not found %s\n" % (templateFilename)
        f = open(templateFilename, 'r')
        template = f.read()
        template = template.replace('${PROJECTNAME_UPPERCASE}', _targetProject.name.upper())
        template = template.replace('${PROJECTNAME}', _targetProject.name)
        f.close()
        
        # don't overwrite the existing file if it contains the same text, because this will trigger a source recompile later!
        if( csnUtility.FileToString(templateOutputFilename) != template ):
            f = open(templateOutputFilename, 'w')
            f.write(template)
            f.close()
        
class Project(object):
    """
    Contains the data for the makefile (or vcproj) for a project.
    Config and use file:
    CMake uses config and use files to let packages use other packages. The config file assigns a number of variables
    such as SAMPLE_APP_INCLUDE_DIRECTORIES and SAMPLE_APP_LIBRARY_DIRECTORIES. The use file uses these values to add
    include directories and library directories to the current CMake target. The standard way to use these files is to a)
    make sure that SAMPLE_APP_DIR points to the location of SAMPLE_APPConfig.cmake and UseSAMPLE_APP.cmake, b) 
    call FIND_PACKAGE(SAMPLE_APP) and c) call INCLUDE(${SAMPLE_APP_USE_FILE}. In step b) the config file of SAMPLE_APP is included and
    in step c) the necessary include directories, library directories etc are added to the current target.
    To adhere to normal CMake procedures, csnBuild also uses the use file and config file. However, FIND_PACKAGE is not needed,
    because we can directly include first the config file and then the use file.
    
    The constructors initialises these member variables:
    self.binarySubfolder -- Direct subfolder - within the binary folder - for this project. Is either 'executable' or 'library'.
    self.installSubfolder -- Direct subfolder - within the install folder - for targets generated by this project.
    self.useBefore -- A list of projects. This project must be used before the projects in this list.
    self.configFilePath -- The config file for the project. See above.
    self.sources -- Sources to be compiled for this target.
    self.sourceGroups -- Dictionary (groupName -> sources) for sources that should be placed in a visual studio group.
    self.rules - CMake rules. See AddRule function.
    self.compileAndLinkConfigFor -- Dictionary (WIN32/NOT WIN32/ALL -> CompileAndLinkConfig) with definitions to be used for different operating systems. 
    self.sourcesToBeMoced -- Sources for which a moc file must be generated.
    self.sourcesToBeUIed -- Sources for which qt's UI.exe must be run.
    self.filesToInstall -- Contains files to be installed in the binary folder. It has the structure filesToInstall[mode][installPath] = files.
    For example: if self.filesToInstall[\"debug\"][\"data\"] = [\"c:/one.txt\", \"c:/two.txt\"], 
    then c:/one.txt and c:/two.txt must be installed in the data subfolder of the binary folder when in debug mode.
    self.useFilePath -- Path to the use file of the project. If it is relative, then the binary folder will be prepended.
    self.cmakeListsSubpath -- The cmake file that builds the project as a target
    self.projects -- Set of related project instances. These projects have been added to self using AddProjects.
    self.projectsNonRequired -- Subset of self.projects. Contains projects that self doesn't depend on.
    self.generateWin32Header -- Flag that says if a standard Win32Header.h must be generated
    self.precompiledHeader -- Name of the precompiled header file. If non-empty, and using Visual Studio (on Windows),
    then precompiled headers is set up.
    The project does not add a Visual Studio dependency on any project in this list.      
    """
    
    def __new__(cls, *a, **b):
        # Get the frame where the instantiation came from
        frame = inspect.stack()[1]
        # Continue with __new__ in super objects
        o = super(Project, cls).__new__(cls, a, b)
        # Save important frame infos in object
        o.debug_call = frame[1]
        return o

    """
    _type -- Type of the project, should be \"executable\", \"library\", \"dll\" or \"third party\".
    _name -- Name of the project, e.g. \"SampleApp\".
    _sourceRootFolder -- If None, then the root folder where source files are located is derived from 
    the call stack. For example, if this class' constructor is called in a file 
    d:/users/me/csnMyProject.py, and you want to configure the files d:/users/me/src/hello.h and 
    d:/users/me/src/hello.cpp with Cmake, then you do not need to pass a value for _sourceRootFolder, 
    because it is inferred from the call stack. 
    """    
    def __init__(self, _name, _type, _sourceRootFolder = None ):
        self.sources = []
        self.sourceGroups = dict()

        configTypes = ConfigTypes()
        self.compileAndLinkConfigFor = dict()
        for opSysName in configTypes.List():
            self.compileAndLinkConfigFor[opSysName] = CompileAndLinkConfig()
        self.compileAndLinkConfigFor[configTypes.win32].private.definitions.append("/Zm200")

        self.precompiledHeader = ""
        self.sourcesToBeMoced = []
        self.sourcesToBeUIed = []
        self.name = _name
        self.filesToInstall = dict()
        self.filesToInstall["debug"] = dict()
        self.filesToInstall["release"] = dict()
        self.type = _type
        self.rules = dict()
        self.createIfNotExistent = dict()
        
        self.sourceRootFolder = _sourceRootFolder
        if self.sourceRootFolder is None:
            file = self.debug_call
            self.sourceRootFolder = csnUtility.ForwardSlashes(os.path.normpath(os.path.dirname(file)))
        self.useBefore = []
        if( self.type == "dll" ):
            self.binarySubfolder = "library/%s" % (_name)
        else:
            self.binarySubfolder = "%s/%s" % (self.type, _name)
        self.installSubFolder = ""
        self.configFilePath = "%s/%sConfig.cmake" % (self.binarySubfolder, _name)
        self.useFilePath = "%s/Use%s.cmake" % (self.binarySubfolder, _name)
        self.cmakeListsSubpath = "%s/CMakeLists.txt" % (self.binarySubfolder)
        self.projects = OrderedSet.OrderedSet()
        self.projectsNonRequired = OrderedSet.OrderedSet()
        self.generateWin32Header = 1

    def AddProjects(self, _projects, _dependency = 1): 
        """ 
        Adds projects in _projects as required projects. If an item in _projects is a function, then
        it is called as a function (the result of the function should be a Project).
        _dependency - Flag that states that self target requires (is dependent on) _projects.
        _private - If true, then the dependency on this project is not propagated to other projects.
        Raises StandardError in case of a cyclic dependency.
        """
        for project in _projects:
            projectToAdd = ToProject(project)
                
            if( self is projectToAdd ):
                raise DependencyError, "Project %s cannot be added to itself" % (projectToAdd.name)
                
            if( not projectToAdd in self.projects ):
                if( _dependency and projectToAdd.DependsOn(self) ):
                    raise DependencyError, "Circular dependency detected during %s.AddProjects(%s)" % (self.name, projectToAdd.name)
                self.projects.add( projectToAdd )
                if( not _dependency ):
                    self.projectsNonRequired.add( projectToAdd )

    def AddSources(self, _listOfSourceFiles, _moc = 0, _ui = 0, _sourceGroup = "", _checkExists = 1, _forceAdd = 0):
        """
        Adds items to self.sources. For each source file that is not an absolute path, self.sourceRootFolder is prefixed.
        Entries of _listOfSourceFiles may contain wildcards, such as src/*/*.h.
        If _moc, then a moc file is generated for each header file in _listOfSourceFiles.
        If _ui, then qt's ui.exe is run for the file.
        If _checkExists, then added sources (possibly after wildcard expansion) must exist on the filesystem, or an exception is thrown.
        _forceAdd - If true, then each item in _listOfSourceFiles is added as a source, even if the item does not exist on the disk.
        """
        for sourceFile in _listOfSourceFiles:
            sources = self.Glob(sourceFile)
            if( _checkExists and not len(sources) ):
                    raise IOError, "Path file not found %s" % (sourceFile)
            if( not len(sources) and _forceAdd ):
                sources = [sourceFile]
            
            for source in sources:
                if _moc and not source in self.sourcesToBeMoced:
                    self.sourcesToBeMoced.append(source)
                
                if( not source in self.sources ):
                    if( _ui ):
                        self.sourcesToBeUIed.append(source)
                    self.sources.append(source)
                    if _sourceGroup != "":
                        if not self.sourceGroups.has_key(_sourceGroup):
                            self.sourceGroups[_sourceGroup] = []
                        self.sourceGroups[_sourceGroup].append(source)
                   
    def AddFilesToInstall(self, _list, _location = None, _debugOnly = 0, _releaseOnly = 0):
        """
        Adds items to self.filesToInstall.
        Entries of _list may contain wildcards, such as lib/*/*.dll.
        You may also include a folder in _list. In that case, the whole folder is copied during
        the install.
        Relative paths in _list are assumed to be relative to the root of the binary folder where the targets 
        are created.
        _debugOnly - If true, then the dll is only installed to the debug install folder.
        _releaseOnly - If true, then the dll is only installed to the release install folder.
        """
        
        if _location is None:
            _location = '.'
            
        for file in _list:
            if not _debugOnly:
                if not self.filesToInstall["release"].has_key(_location):
                    self.filesToInstall["release"][_location] = []
                if not file in self.filesToInstall["release"][_location]:
                    self.filesToInstall["release"][_location].append( file )
            if not _releaseOnly:
                if not self.filesToInstall["debug"].has_key(_location):
                    self.filesToInstall["debug"][_location] = []
                if not file in self.filesToInstall["debug"][_location]:
                    self.filesToInstall["debug"][_location].append( file )
                
    def AddDefinitions(self, _listOfDefinitions, _private = 0, _WIN32 = 0, _NOT_WIN32 = 0 ):
        """
        Adds definitions to self.compileAndLinkConfigFor. 
        """
        configTypes = ConfigTypes()
        opSystemName = configTypes.GetOpSysName(_WIN32, _NOT_WIN32)            
        compileAndLinkConfig = self.compileAndLinkConfigFor[opSystemName]
        if( _private ):
            compileAndLinkConfig.private.definitions.extend(_listOfDefinitions)
        else:
            compileAndLinkConfig.public.definitions.extend(_listOfDefinitions)
        
    def AddIncludeFolders(self, _listOfIncludeFolders):
        """
        Adds items to self.publicIncludeFolders. 
        If an item has a relative path, then it will be prefixed with _sourceRootFolder.
        Added include paths must exist on the filesystem.
        If an item in _listOfIncludeFolders has wildcards, all matching folders will be added to the list.
        """
        configTypes = ConfigTypes()
        defaultCompileAndLinkConfig = self.compileAndLinkConfigFor[configTypes.all]
        for includeFolder in _listOfIncludeFolders:
            for folder in self.Glob(includeFolder):
                if (not os.path.exists(folder)) or os.path.isdir(folder):
                    defaultCompileAndLinkConfig.public.includeFolders.append( folder )
        
    def SetPrecompiledHeader(self, _precompiledHeader):
        """
        If _precompiledHeader is not "", then precompiled headers are used in Visual Studio (Windows) with
        this filename. 
        """
        globResult = self.Glob(_precompiledHeader)
        assert len(globResult) == 1, "Error locating precompiled header file %s (source root folder = %s)" % (_precompiledHeader, self.sourceRootFolder)
        self.precompiledHeader = globResult[0]
        self.AddSources([_precompiledHeader], _sourceGroup = "PCH Files (header)")
        
    def AddLibraryFolders(self, _listOfLibraryFolders):
        """
        Adds items to self.publicLibraryFolders. 
        If an item has a relative path, then it will be prefixed with _sourceRootFolder.
        Added library paths must exist on the filesystem.
        """
        configTypes = ConfigTypes()
        defaultCompileAndLinkConfig = self.compileAndLinkConfigFor[configTypes.all]
        for libraryFolder in _listOfLibraryFolders:
            defaultCompileAndLinkConfig.public.libraryFolders.append( self.__FindPath(libraryFolder) )
        
    def AddLibraries(self, _listOfLibraries, _WIN32 = 0, _NOT_WIN32 = 0, _debugOnly = 0, _releaseOnly = 0):
        """
        Adds items to self.publicLibraries. 
        """
        assert not( _debugOnly and _releaseOnly)
        type = "" # empty string is the default, meaning both debug and release
        if _debugOnly:
            type = "debug"
        if _releaseOnly:
            type = "optimized"

        configTypes = ConfigTypes()
        opSysName = configTypes.GetOpSysName(_WIN32, _NOT_WIN32)
        compileAndLinkConfig = self.compileAndLinkConfigFor[opSysName]            
            
        for library in _listOfLibraries:
            compileAndLinkConfig.public.libraries.append("%s %s" % (type, library))
        
    def __FindPath(self, _path):
        """ 
        Tries to locate _path as an absolute path or as a path relative to self.sourceRootFolder. 
        Returns an absolute path, containing only forward slashes.
        Throws IOError if path was not found.
        """
        path = os.path.normpath(_path)
        if( not os.path.isabs(path) ):
            path = os.path.abspath("%s/%s" % (self.sourceRootFolder, path))
        if( not os.path.exists(path) ):
            raise IOError, "Path file not found %s (tried %s)" % (_path, path)
            
        path = csnUtility.ForwardSlashes(path)
        return path
        
    def PrependSourceRootFolderToRelativePath(self, _path):
        """ 
        Returns _path prepended with self.sourceRootFolder, unless _path is already an absolute path (in that case, _path is returned).
        """
        path = csnUtility.ForwardSlashes(_path)
        if not os.path.isabs(path):
            path = os.path.abspath("%s/%s" % (self.sourceRootFolder, path))
        return csnUtility.ForwardSlashes(path)
    
    def Glob(self, _path):
        """ 
        Returns a list of files that match _path (which can be absolute, or relative to self.sourceRootFolder). 
        The return paths are absolute, containing only forward slashes.
        """
        return [csnUtility.ForwardSlashes(x) for x in glob.glob(self.PrependSourceRootFolderToRelativePath(_path))]
    
    def DependsOn(self, _otherProject, _skipList = None):
        """ 
        Returns true if self is (directly or indirectly) dependent upon _otherProject. 
        _otherProject - May be a project, or a function returning a project.
        _skipList - Used to not process project twice during the recursion (also prevents infinite loops).
        """
        if _skipList is None:
            _skipList = []
        
        otherProject = ToProject(_otherProject)
        assert not self in _skipList, "%s should not be in stoplist" % (self.name)
        _skipList.append(self)
        for requiredProject in self.RequiredProjects():
            if requiredProject in _skipList:
                continue
            if requiredProject is otherProject or requiredProject.DependsOn(otherProject, _skipList ):
                return 1
        return 0
        
    def RequiredProjects(self, _recursive = 0):
        """
        Return a set of projects that self depends upon.
        If recursive is true, then required projects of required projects are also retrieved.
        """
        result = self.projects - self.projectsNonRequired

        if( _recursive ):
            moreResults = OrderedSet.OrderedSet()
            for project in result:
                moreResults.update( project.RequiredProjects(_recursive) )
            result.update(moreResults)
        return result
        
    def AllProjects(self, _recursive = 0, _skipList = None):
        """
        Returns list of all projects associated with this project.
        """
        result = OrderedSet.OrderedSet()
        result.update(self.projects)
        if( _recursive ):
            moreResults = OrderedSet.OrderedSet()
            for project in result:
                # see if project is in the skip list
                if _skipList is None:
                    _skipList = []
                if project in _skipList:
                    continue
                # add project to the skip list, and recurse
                _skipList.append(project)
                moreResults.update( project.AllProjects(_recursive, _skipList) )
            result.update(moreResults)
        return result
        
    def UseBefore(self, _otherProject):
        """ 
        Indicate that self must be used before _otherProjects in a cmake file. 
        Throws DependencyError if _otherProject wants to be used before self.
        _otherProject - May be a project, or a function returning a project.
        """
        otherProject = ToProject(_otherProject)
        if( otherProject.WantsToBeUsedBefore(self) ):
            raise DependencyError, "Cyclic use-before relation between %s and %s" % (self.name, otherProject.name)
        self.useBefore.append(otherProject)
        
    def WantsToBeUsedBefore(self, _otherProject):
        """ 
        Return true if self wants to be used before _otherProject.
        _otherProject - May be a project, or a function returning a project.
        """
        otherProject = ToProject(_otherProject)
        if( self is otherProject ):
            return 0
            
        if( otherProject in self.useBefore ):
            return 1
            
        for requiredProject in self.RequiredProjects(1):
            if( otherProject in requiredProject.useBefore ):
                return 1
                
        return 0
           
    def ProjectsToUse(self):
        """
        Determine a list of projects that must be used (meaning: include the config and use file) to generate this project.
        Note that self is also included in this list.
        The list is sorted in the correct order, using Project.WantsToBeUsedBefore.
        """
        result = []
        
        projectsToUse = [project for project in self.RequiredProjects(_recursive = 1)]
        assert not self in projectsToUse, "%s should not be in projectsToUse" % (self.name)
        projectsToUse.append(self)
        
        (count, maxCount) = (0, 1)
        for i in range(len(projectsToUse)):
            maxCount = maxCount * (i+1)
        
        while (len(projectsToUse)):
            assert count < maxCount
            count += 1
            project = projectsToUse.pop()

            # check if we must skip this project for now, because another project must be used before this one
            skipThisProjectForNow = 0
            for otherProject in projectsToUse:
                if( otherProject.WantsToBeUsedBefore(project) ):
                    skipThisProjectForNow = 1
            if( skipThisProjectForNow ):
                projectsToUse.insert(0, project)
                continue
            else:
                result.append(project)
          
        return result
        
    def GenerateConfigFile(self, _binaryFolderForCSnake, _public):
        """
        Generates the XXXConfig.cmake file for this project.
        _public - If true, generates a config file that can be used in any cmake file. If false,
        it generates the private config file that is used in the csnake-generated cmake files.
        """
        fileConfig = self.GetPathToConfigFile(_binaryFolderForCSnake, _public)
        f = open(fileConfig, 'w')
        
        configTypes = ConfigTypes()
        defaultCompileAndLinkConfig = self.compileAndLinkConfigFor[configTypes.all]
        
        # create list with folder where libraries should be found. Add the bin folder where all the
        # targets are placed to this list. 
        publicLibraryFolders = defaultCompileAndLinkConfig.public.libraryFolders
        if _public:
            targetProjectInstallSubfolder = "%s/%s" % (_binaryFolderForCSnake, self.installSubFolder)
            publicLibraryFolders.append(targetProjectInstallSubfolder) 

        # write header and some cmake fields
        f.write( "# File generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "SET( %s_FOUND \"TRUE\" )\n" % (self.name) )
        f.write( "SET( %s_USE_FILE \"%s\" )\n" % (self.name, self.GetPathToUseFile(_binaryFolderForCSnake) ) )
        f.write( "SET( %s_INCLUDE_DIRS %s )\n" % (self.name, csnUtility.Join(defaultCompileAndLinkConfig.public.includeFolders, _addQuotes = 1)) )
        f.write( "SET( %s_LIBRARY_DIRS %s )\n" % (self.name, csnUtility.Join(publicLibraryFolders, _addQuotes = 1)) )
        for opSysName in [configTypes.win32, configTypes.notWin32]:
            compileAndLinkConfig = self.compileAndLinkConfigFor[opSysName]
            if( len(compileAndLinkConfig.public.libraries) ):
                f.write( "IF(%s)\n" % (opSysName))
                f.write( "SET( %s_LIBRARIES %s )\n" % (self.name, csnUtility.Join(compileAndLinkConfig.public.libraries, _addQuotes = 1)) )
                f.write( "ENDIF(%s)\n" % (opSysName))
        defaultCompileAndLinkConfig = self.compileAndLinkConfigFor[configTypes.all]
        if( len(defaultCompileAndLinkConfig.public.libraries) ):
            f.write( "SET( %s_LIBRARIES ${%s_LIBRARIES} %s )\n" % (self.name, self.name, csnUtility.Join(defaultCompileAndLinkConfig.public.libraries, _addQuotes = 1)) )

        # add the target of this project to the list of libraries that should be linked
        if _public and len(self.sources) > 0 and (self.type == "library" or self.type == "dll"):
            targetName = self.name
            f.write( "SET( %s_LIBRARIES ${%s_LIBRARIES} %s )\n" % (self.name, self.name, csnUtility.Join([targetName], _addQuotes = 1)) )
                
    def GenerateUseFile(self, _binaryFolderForCSnake):
        """
        Generates the UseXXX.cmake file for this project.
        """
        fileUse = "%s/%s" % (_binaryFolderForCSnake, self.useFilePath)
        f = open(fileUse, 'w')
        configTypes = ConfigTypes()
        
        # write header and some cmake fields
        f.write( "# File generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "INCLUDE_DIRECTORIES(${%s_INCLUDE_DIRS})\n" % (self.name) )
        f.write( "LINK_DIRECTORIES(${%s_LIBRARY_DIRS})\n" % (self.name) )
        
        # write definitions     
        for opSysName in [configTypes.win32, configTypes.notWin32]:
            compileAndLinkConfig = self.compileAndLinkConfigFor[opSysName]
            if( len(compileAndLinkConfig.public.definitions) ):
                f.write( "IF(%s)\n" % (opSysName))
                f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(compileAndLinkConfig.public.definitions) )
                f.write( "ENDIF(%s)\n" % (opSysName))
        defaultCompileAndLinkConfig = self.compileAndLinkConfigFor[configTypes.all]
        if( len(defaultCompileAndLinkConfig.public.definitions) ):
            f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(defaultCompileAndLinkConfig.public.definitions) )
   
        # write definitions that state whether this is a static library
        #if self.type == "library":
        #    f.write( "ADD_DEFINITIONS(%sSTATIC)\n" % self.name )
            
    def GetPathToConfigFile(self, _binaryFolderForCSnake, _public):
        """ 
        Returns self.useFilePath if it is absolute. Otherwise, returns _binaryFolderForCSnake + self.useFilePath.
        If _public is false, and the project is not of type 'third party', then the postfix ".private" 
        is added to the return value.
        """
        if( os.path.isabs(self.configFilePath) ):
            result = self.configFilePath
        else:
            result = "%s/%s" % (_binaryFolderForCSnake, self.configFilePath)

        postfix = ""
        if (not self.type == "third party") and (not _public):
            postfix = ".private"
             
        return result + postfix


    def GetPathToUseFile(self, _binaryFolderForCSnake):
        """ 
        Returns self.useFilePath if it is absolute. Otherwise, returns _binaryFolderForCSnake + self.useFilePath.
        """
        if( os.path.isabs(self.useFilePath) ):
            return self.useFilePath
        else:
            return "%s/%s" % (_binaryFolderForCSnake, self.useFilePath)
        
    def ResolvePathsOfFilesToInstall(self, _thirdPartyBinFolder, _skipCVS = 1):
        """ 
        This function replaces relative paths and wildcards in self.filesToInstall with absolute paths without wildcards.
        _skipCVS - If true, folders called CVS are automatically skipped. 
        """
        for mode in ("debug", "release"):
            for project in self.AllProjects(_recursive = 1):
                for location in project.filesToInstall[mode].keys():
                    newList = []
                    for dllPattern in project.filesToInstall[mode][location]:
                        path = csnUtility.ForwardSlashes(dllPattern)
                        if not os.path.isabs(path):
                            path = "%s/%s" % (_thirdPartyBinFolder, path)
                        for dll in glob.glob(path):
                            skip = (os.path.basename(dll) == "CVS" and _skipCVS and os.path.isdir(dll))
                            if not skip:
                                newList.append(dll)
                    project.filesToInstall[mode][location] = newList
    
    def SetGenerateWin32Header(self, _flag):
        self.generateWin32Header = _flag

    def GetGenerateWin32Header(self):
        return self.generateWin32Header
                   
    def CreateCMakeSection_IncludeConfigAndUseFiles(self, f, binaryFolder):
        """ Include the use file and config file for any dependency project, and finally also
        add the use and config file for this project (do this last, so that all definitions from
        the dependency projects are already included).
        """
        projectsToUse = [project for project in self.RequiredProjects(_recursive = 1)]
        assert not self in projectsToUse, "%s should not be in projectsToUse" % (self.name)
        projectsToUse.append(self)
        for project in projectsToUse:
            f.write( "\n# use %s\n" % (project.name) )
            f.write( "INCLUDE(\"%s\")\n" % (project.GetPathToConfigFile(binaryFolder, _public = (self.name != project.name and not IsRunningOnWindows())) ))
            f.write( "INCLUDE(\"%s\")\n" % (project.GetPathToUseFile(binaryFolder)) )
    
    def CreateCMakeSection_SourceGroups(self, f):
        for groupName in self.sourceGroups:
            f.write( "\n # Create %s group \n" % groupName )
            f.write( "IF (WIN32)\n" )
            f.write( "  SOURCE_GROUP(\"%s\" FILES %s)\n" % (groupName, csnUtility.Join(self.sourceGroups[groupName], _addQuotes = 1)))
            f.write( "ENDIF(WIN32)\n\n" )
    
    def CreateCMakeSection_MocRules(self, f):
        cmakeMocInputVar = ""
        if( len(self.sourcesToBeMoced) ):
            cmakeMocInputVarName = "MOC_%s" % (self.name)
            cmakeMocInputVar = "${%s}" % (cmakeMocInputVarName)
            f.write("\nQT_WRAP_CPP( %s %s %s )\n" % (self.name, cmakeMocInputVarName, csnUtility.Join(self.sourcesToBeMoced, _addQuotes = 1)) )
            # write section for sorting moc files in a separate folder in Visual Studio
            f.write( "\n # Create MOC group \n" )
            f.write( "IF (WIN32)\n" )
            f.write( "  SOURCE_GROUP(\"Generated MOC Files\" REGULAR_EXPRESSION moc_[a-zA-Z0-9_]*[.]cxx$)\n")
            f.write( "ENDIF(WIN32)\n\n" )
        return cmakeMocInputVar
    
    def CreateCMakeSection_UicRules(self, f):
        cmakeUIHInputVar = ""
        cmakeUICppInputVar = ""
        if( len(self.sourcesToBeUIed) ):
            cmakeUIHInputVarName = "UI_H_%s" % (self.name)
            cmakeUIHInputVar = "${%s}" % (cmakeUIHInputVarName)
            cmakeUICppInputVarName = "UI_CPP_%s" % (self.name)
            cmakeUICppInputVar = "${%s}" % (cmakeUICppInputVarName)
            f.write("\nQT_WRAP_UI( %s %s %s %s )\n" % (self.name, cmakeUIHInputVarName, cmakeUICppInputVarName, csnUtility.Join(self.sourcesToBeUIed, _addQuotes = 1)) )
            # write section for sorting ui files in a separate folder in Visual Studio
            f.write( "\n # Create UI group \n" )
            f.write( "IF (WIN32)\n" )
            f.write( "  SOURCE_GROUP(\"Forms\" REGULAR_EXPRESSION [.]ui$)\n")
            f.write( "ENDIF(WIN32)\n\n" )
        return (cmakeUIHInputVar, cmakeUICppInputVar)
    
    def CreateCMakeSection_Definitions(self, f):
        configTypes = ConfigTypes()
        for opSysName in [configTypes.win32, configTypes.notWin32]:
            compileAndLinkConfig = self.compileAndLinkConfigFor[opSysName]
            if( len(compileAndLinkConfig.private.definitions) ):
                f.write( "IF(%s)\n" % (opSysName))
                f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(compileAndLinkConfig.private.definitions) )
                f.write( "ENDIF(%s)\n" % (opSysName))
        if( len(self.compileAndLinkConfigFor[configTypes.all].private.definitions) ):
            f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(self.compileAndLinkConfigFor[configTypes.all].private.definitions) )

    def CreateCMakeSection_Sources(self, f, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar):
        if(self.type == "executable" ):
            f.write( "ADD_EXECUTABLE(%s %s %s %s %s)\n" % (self.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(self.sources, _addQuotes = 1)) )
            
        elif(self.type == "library" ):
            f.write( "ADD_LIBRARY(%s STATIC %s %s %s %s)\n" % (self.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(self.sources, _addQuotes = 1)) )
        
        elif(self.type == "dll" ):
            f.write( "ADD_LIBRARY(%s SHARED %s %s %s %s)\n" % (self.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(self.sources, _addQuotes = 1)) )
            
        else:
            raise NameError, "Unknown project type %s" % self.type
        
    def CreateCMakeSection_InstallRules(self, f, _installFolder):
        if( _installFolder != "" and self.type != "library"):
            destination = "%s/%s" % (_installFolder, self.installSubFolder)
            f.write( "\n# Rule for installing files in location %s\n" % destination)
            f.write( "INSTALL(TARGETS %s DESTINATION %s)\n" % (self.name, destination) )
    
    def CreateCMakeSection_Rules(self, f):
        for description, rule in self.rules.iteritems():
            f.write("\n#Adding rule %s\n" % description)
            f.write("ADD_CUSTOM_COMMAND( TARGET %s PRE_BUILD COMMAND %s WORKING_DIRECTORY \"%s\" COMMENT \"Running rule %s\" VERBATIM )\n" % (self.name, rule.command, rule.workingDirectory, description))
    
    def CreateCMakeSection_Link(self, f):
        if self.type in ("dll", "executable"):
            targetLinkLibraries = ""
            for project in self.RequiredProjects(_recursive = 1):
                if project.type == "third party":
                    continue
                targetLinkLibraries = targetLinkLibraries + ("${%s_LIBRARIES} " % project.name) 
            f.write( "TARGET_LINK_LIBRARIES(%s %s)\n" % (self.name, targetLinkLibraries) )
        
    def CreateCMakeSections(self, f, _binaryFolderForCSnake, _installFolder):
        """ Writes different CMake sections for this project to the file f. """
    
        self.CreateCMakeSection_IncludeConfigAndUseFiles(f, _binaryFolderForCSnake)
        self.CreateCMakeSection_SourceGroups(f)
        cmakeMocInputVar = self.CreateCMakeSection_MocRules(f)
        (cmakeUIHInputVar, cmakeUICppInputVar) = self.CreateCMakeSection_UicRules(f)
            
        # write section that is specific for the project type   
        if( len(self.sources) ):
            f.write( "\n# Add target\n" )
            self.CreateCMakeSection_Sources(f, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar)
            self.CreateCMakeSection_Link(f)
            self.CreateCMakeSection_Definitions(f)
            self.CreateCMakeSection_InstallRules(f, _installFolder)
            self.CreateCMakeSection_Rules(f)

    def CreateExtraSourceFilesForTesting(self, _binaryFolderForCSnake):
        """ 
        Tests if this project is a test project. If so, checks if the test runner output file exists. If not, creates a dummy file.
        This dummy file is needed, for otherwise CMake will not include the test runner source file in the test project.
        """
        if hasattr(self, "testRunnerSourceFile"):
            projectBinFolderForCSnake = self.AbsoluteBinaryFolder(_binaryFolderForCSnake) 
            testRunnerSourceFile = "%s/%s" % (projectBinFolderForCSnake, self.testRunnerSourceFile)
            if not os.path.exists(testRunnerSourceFile):
                f = open(testRunnerSourceFile, 'w')
                f.write("// Test runner source file. To be created by CxxTest.py.")
                f.close()
        
    def AddRule(self, description, command, workingDirectory = "."):
        """
        Adds a new rule to the self.rules dictionary, using description as the key.
        """
        rule = Rule()
        rule.command = command
        rule.workingDirectory = workingDirectory
        self.rules[description] = rule
        
    def CreateTestProject(self, _cxxTestProject, _enableWxWidgets = 0):
        """
        Creates a test project in self.testProject. This testProject will be configured by CMake, and will run the tests for this
        project (i.e. for self).
        _cxxTestProject - May be the cxxTest project instance, or a function returning a cxxTest project instance.
        _enableWxWidgets - If true, the CMake rule that creates the testrunner will create a test runner that initializes wxWidgets, so that
        your tests can create wxWidgets objects.
        """
        cxxTestProject = ToProject(_cxxTestProject)
        self.testProject = Project("%sTest" % self.name, "executable", _sourceRootFolder = self.sourceRootFolder)
        self.testProject.testRunnerSourceFile = "%s.cpp" % self.testProject.name
        pythonScript = "%s/CxxTest/cxxtestgen.py" % cxxTestProject.sourceRootFolder
        self.testProject.AddSources([self.testProject.testRunnerSourceFile], _checkExists = 0, _forceAdd = 1)
        self.testProject.AddDefinitions(["/DCXXTEST_HAVE_EH"], _private = 1, _WIN32 = 1)
        self.testProject.AddDefinitions(["-DCXXTEST_HAVE_EH"], _private = 1, _NOT_WIN32 = 1)
        
        # todo: find out where python is located
        wxRunnerArg = ""
        if _enableWxWidgets:
            wxRunnerArg = "--template \"%s\"" % (csnUtility.GetRootOfCSnake() + "/TemplateSourceFiles/wxRunner.tpl")
        self.testProject.AddRule("Create test runner", "\"%s\" %s %s --have-eh --error-printer -o %s " % (csnUtility.ForwardSlashes(pythonPath), pythonScript, wxRunnerArg, self.testProject.testRunnerSourceFile))
        self.testProject.AddProjects([cxxTestProject, self])
        self.AddProjects([self.testProject], _dependency = 0)
        
    def AddTests(self, listOfTests, _cxxTestProject, _enableWxWidgets = 0):
        """
        _cxxTestProject - May be the cxxTest project instance, or a function returning a cxxTest project instance.
        """
        cxxTestProject = ToProject(_cxxTestProject)
        
        if not hasattr(self, "testProject"):
            self.CreateTestProject(cxxTestProject, _enableWxWidgets)
            
        rule = self.testProject.rules["Create test runner"]
        for test in listOfTests:
            absPathToTest = self.PrependSourceRootFolderToRelativePath(test)
            rule.command += "\"%s\"" % absPathToTest
            self.testProject.AddSources([absPathToTest], _checkExists = 0)

    def AbsoluteBinaryFolder(self, _rootBinaryFolder):
        """
        Returns the bin folder for storing binary files for this project.
        _rootBinFolder - The binary folder for building the entire solution.
        """
        return _rootBinaryFolder + "/" + self.binarySubfolder

    def WriteDependencyStructureToXML(self, filename):
        f = open(filename, 'w')
        self.WriteDependencyStructureToXMLImp(f)
        f.close()

    def WriteDependencyStructureToXMLImp(self, f, indent = 0):
        for i in range(indent):
            f.write(' ')
        f.write("<%s>" % self.name)
        for project in self.RequiredProjects():
            project.WriteDependencyStructureToXMLImp(f, indent + 4)
        f.write("</%s>\n" % self.name)
