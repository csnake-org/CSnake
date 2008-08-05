import csnUtility
import csnVisualStudio2003
import csnKDevelop
import inspect
import os.path
import warnings
import sys
import re
import glob
import types
import GlobDirectoryWalker
import OrderedSet

# General documentation
#
# This block contains an introduction to the CSnake code. It's main purpose is to introduce some common terminology and concepts.
#  It is assumed that the reader has already read the CSnake user manual.
#
# Terminology:
# target project - Project that you want to build with CSnake. Modelled by class csnBuild.Project.
# dependency project - Project that must also be built in order to built the target project. Modelled by class csnBuild.Project.
# build folder - Folder where all intermediate build results (CMakeCache.txt, .obj files, etc) are stored for the target project and all dependency projects.
# binary folder - Folder where all final build results (executables, dlls etc) are stored.
# install folder - Folder to which the build results are copied, and from which you can run the application. Note that CSnake allows you to use the build folder as the install folder as well.
# configuration name - Identifies a build configuration, such as "Debug" or "Release". The name "DebugAndRelease" means that both Debug and Release must be generated.
# source root folder - Folder used for locating the source files for a project. When adding sources to a project, names relative to the source root folder may be used.
#
# Config and use file:
# CMake uses config and use files to let packages use other packages. The config file assigns a number of variables
# such as SAMPLE_APP_INCLUDE_DIRECTORIES and SAMPLE_APP_LIBRARY_DIRECTORIES. The use file uses these values to add
# include directories and library directories to the current CMake target. The standard way to use these files is to a)
# make sure that SAMPLE_APP_DIR points to the location of SAMPLE_APPConfig.cmake and UseSAMPLE_APP.cmake, b) 
# call FIND_PACKAGE(SAMPLE_APP) and c) call INCLUDE(${SAMPLE_APP_USE_FILE}. In step b) the config file of SAMPLE_APP is included and
# in step c) the necessary include directories, library directories etc are added to the current target.
# To adhere to normal CMake procedures, csnBuild also uses the use file and config file. However, FIND_PACKAGE is not needed,
# because the Generator class will directly include the config and use file for any dependency project.
#
# Compilers
#
# In this version of CSnake, you are required to specify the compiler that you will use to build your project. Examples of compiler instances are csnKDevelop.Compiler and csnVisualStudio2003.Compiler.
# I choose this design because it allowed me to simplify the code a lot. For example, when adding a compiler definition for linux, a check is performed to see if the project uses a linux compiler; it not,
# the definition is simply ignored.
# The default compiler is stored in csnBuild.globalCurrentCompilerType. If you create a Project without specifying a compiler, then this compiler will be assigned to the project instance.
#

# ToDo:
# - check that of all root folders, only one contains csnCISTIBToolkit
# - Have public and private related projects (hide the include paths from its clients)
# - If ITK doesn't implement the DONT_INHERIT keyword, then use environment variables to work around the cmake propagation behaviour
# - csn python modules can contain option widgets that are loaded into CSnakeGUI! Use this to add selection of desired toolkit modules in csnGIMIAS
# - Fix module reloading
# - GUI: recently used csnakesettings files.
# - Better GUI: do more checks, give nice error messages
# - If copy_tree copies nothing, check that the source folder is empty
# - On linux, prevent building with all, force use of either debug or release
# - On linux, don't copy any windows dlls
# End: ToDo.

# add root of csnake to the system path
sys.path.append(csnUtility.GetRootOfCSnake())

# set default location of python. Note that this path may be overwritten in csnGUIHandler
# \todo: Put this global variable in a helper struct, to make it more visible.
pythonPath = "D:/Python24/python.exe"

# Set default method for creating a csnCompiler.Compiler instance.
globalCurrentCompilerType = csnVisualStudio2003.Compiler

class DependencyError(StandardError):
    """ Used when there is a cyclic dependency between CSnake projects. """
    pass
    
class SyntaxError(StandardError):
    """ Used when there is a syntax error, for example in a folder name. """
    pass

class Rule:
    """ This class contains a build rule for e.g. Visual Studio, Make, etc """
    def __init__(self):
        self.workingDirectory = ""
        self.command = ""

def ToProject(project):
    """
    Helper function that tests if its argument (project) is a function. If so, it returns the result of the function. 
    If not, it returns its argument (project). It is used to treat Project instances and functions returning a Project instance
    in the same way.
    """
    result = project
    if type(project) == types.FunctionType:
        result = project()
    return result

class Generator:
    """
    Generates the CMakeLists.txt for a csnBuild.Project and all its dependency projects.
    """

    def Generate(self, _targetProject, _buildFolder, _installFolder = "", _configurationName = "DebugAndRelease", _generatedList = None):
        """
        Generates the CMakeLists.txt for _targetProject (a csnBuild.Project) in _buildFolder.
        _installFolder -- Install rules are added to the CMakeLists to install files in this folder.
        _configurationName -- If "DebugAndRelease", then a Debug and a Release configuration are generated (works with Visual Studio),
        if "Debug" or "Release", then only a single configuration is generated (works with KDevelop and Unix Makefiles).
        _generatedList -- List of projects for which Generate was already called (internal to the function).
        """

        isTopLevelProject = _generatedList is None
        if( isTopLevelProject ):
            _generatedList = []

        # trying to Generate a project twice indicates a logical error in the code        
        assert not _targetProject in _generatedList, "Target project name = %s" % (_targetProject.name)

        for generatedProject in _generatedList:
            if generatedProject.name == _targetProject.name:
                raise NameError, "Each project must have a unique name. Conflicting projects are %s (in folder %s) and %s (in folder %s)\n" % (_targetProject.name, _targetProject.sourceRootFolder, generatedProject.name, generatedProject.sourceRootFolder)
        _generatedList.append(_targetProject)
        
        # check for backward slashes
        if csnUtility.HasBackSlash(_buildFolder):
            raise SyntaxError, "Error, backslash found in binary folder %s" % _buildFolder
        
        # check  trying to build a third party library
        if( _targetProject.type == "third party" ):
            warnings.warn( "CSnake warning: you are trying to generate CMake scripts for a third party module (nothing generated)\n" )
            return
         
        # set build folder in all compiler instances
        if( isTopLevelProject ):
            _targetProject.compiler.SetBuildFolder(_buildFolder)
            for project in _targetProject.GetProjects(_recursive = True):
                project.compiler.SetBuildFolder(_buildFolder)
                
        # create binary project folder
        os.path.exists(_targetProject.GetBuildFolder()) or os.makedirs(_targetProject.GetBuildFolder())
    
        # create Win32Header
        if( _targetProject.type != "executable" and _targetProject.GetGenerateWin32Header() ):
            self.__GenerateWin32Header(_targetProject)
            # add search path to the generated win32 header
            if not _targetProject.GetBuildFolder() in _targetProject.compiler.public.includeFolders:
                _targetProject.compiler.public.includeFolders.append(_targetProject.GetBuildFolder())
        
        # open cmakelists.txt
        f = open(_targetProject.GetCMakeListsFilename(), 'w')
        
        # write header and some cmake fields
        f.write( "# CMakeLists.txt generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "PROJECT(%s)\n" % (_targetProject.name) )
        f.write( "SET( BINARY_DIR \"%s\")\n" % (_targetProject.compiler.GetOutputFolder(_configurationName)) )

        if not _configurationName == "DebugAndRelease":
            f.write( "SET( CMAKE_BUILD_TYPE %s )\n" % (_configurationName) )
        
        f.write( "\n# All binary outputs are written to the same folder.\n" )
        f.write( "SET( CMAKE_SUPPRESS_REGENERATION TRUE )\n" )
        f.write( "SET( EXECUTABLE_OUTPUT_PATH \"%s\")\n" % _targetProject.GetBinaryInstallFolder(_configurationName) )
        f.write( "SET( LIBRARY_OUTPUT_PATH \"%s\")\n" % _targetProject.GetBinaryInstallFolder(_configurationName) )
    
        # create config and use files, and include them
        _targetProject.GenerateConfigFile( _public = 0)
        _targetProject.GenerateConfigFile( _public = 1)
        _targetProject.GenerateUseFile()
        
        _targetProject.CreateCMakeSections(f, _installFolder)
        _targetProject.RunCustomCommands()

        # Find projects that must be generated. A separate list is used to ease debugging.
        projectsToGenerate = OrderedSet.OrderedSet()
        requiredProjects = _targetProject.GetProjects(_recursive = 1, _onlyRequiredProjects = 1)        
        for projectToGenerate in requiredProjects:
            # determine if we must Generate the project. If a required project will generate it, 
            # then leave it to the required project. This will prevent multiple generation of the same project.
            # If a non-required project will generate it, then still generate the project 
            # (the non-required project may depend on target project to generate project, creating a race condition).
            generateProject = not projectToGenerate in _generatedList and projectToGenerate.type in ("dll", "executable", "library")
            if( generateProject ):
                for requiredProject in _targetProject.GetProjects(_recursive = 0, _onlyRequiredProjects = 1):
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
                f.write( "ADD_SUBDIRECTORY(\"%s\" \"%s\")\n" % (project.GetBuildFolder(), project.GetBuildFolder()) )
                self.Generate(project, _buildFolder, _installFolder, _configurationName, _generatedList)
           
        # add dependencies
        f.write( "\n" )
        for project in requiredProjects:
            staticLibUsingAnotherLib = _targetProject.type == "library" and project.type != "executable" 
            noSources = len(project.sources) == 0 
            if (csnUtility.IsRunningOnWindows() and staticLibUsingAnotherLib) or noSources: 
                continue
            else:
                f.write( "ADD_DEPENDENCIES(%s %s)\n" % (_targetProject.name, project.name) )

        # if top level project, add install rules for all the filesToInstall
        if isTopLevelProject:
            for mode in ("Debug", "Release"):
                for project in _targetProject.ProjectsToUse():
                    # iterate over filesToInstall to be copied in this mode
                    for location in project.filesToInstall[mode].keys():
                        files = ""
                        for file in project.filesToInstall[mode][location]:
                            files += "%s " % csnUtility.NormalizePath(file)
                        if files != "":
                            destination = "%s/%s" % (_installFolder, location)
                            f.write( "\n# Rule for installing files in location %s\n" % destination)
                            f.write("INSTALL(FILES %s DESTINATION %s CONFIGURATIONS %s)\n" % (files, destination, mode.upper()))
                        
        f.close()

    def PostProcess(self, _targetProject, _buildFolder, _kdevelopProjectFolder = ""):
        """
        Apply post-processing after the CMake generation for _targetProject and all its child projects.
        _kdevelopProjectFolder - If generating a KDevelop project, then the KDevelop project file will be
        copied from the bin folder to this folder. This is work around for a problem in 
        KDevelop: it does not show the source tree if the kdevelop project file is in the bin folder.
        """
        projects = OrderedSet.OrderedSet()
        projects.add(_targetProject)
        projects.update( _targetProject.GetProjects(_recursive = 1) )
        ppVisualStudio = csnVisualStudio2003.PostProcessor()
        ppKDevelop = csnKDevelop.PostProcessor()
        for project in projects:
            ppVisualStudio.Do(project, _buildFolder)
        ppKDevelop.Do(_targetProject, _buildFolder, _kdevelopProjectFolder)
    
    def __GenerateWin32Header(self, _targetProject):
        """
        Generates the ProjectNameWin32.h header file for exporting/importing dll functions.
        """
        templateFilename = csnUtility.GetRootOfCSnake() + "/TemplateSourceFiles/Win32Header.h"
        if( _targetProject.type == "library" ):
            templateFilename = csnUtility.GetRootOfCSnake() + "/TemplateSourceFiles/Win32Header.lib.h"
        templateOutputFilename = "%s/%sWin32Header.h" % (_targetProject.GetBuildFolder(), _targetProject.name)
        
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
    self.filesToInstall -- Contains files to be installed in the binary folder. It has the structure filesToInstall[mode][installPath] = files.
    For example: if self.filesToInstall[\"Debug\"][\"data\"] = [\"c:/one.txt\", \"c:/two.txt\"], 
    then c:/one.txt and c:/two.txt must be installed in the data subfolder of the install folder when in debug mode.
    self.useFilePath -- Path to the use file of the project. If it is relative, then the build folder will be prepended.
    self.cmakeListsSubpath -- Path to the cmake file (relative to the build folder) that builds this project.
    self.projects -- Set of related project instances. These projects have been added to self using AddProjects.
    self.projectsNonRequired -- Subset of self.projects. Contains projects that self doesn't depend on.
    The project does not add a dependency on any project in this list.      
    self.generateWin32Header -- Flag that says if a standard Win32Header.h must be generated
    self.precompiledHeader -- Name of the precompiled header file. If non-empty, and using Visual Studio (on Windows),
    then precompiled headers are used for this project.
    self.customCommands -- List of extra commands that must be run when configuring this project.
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
    _sourceRootFolder -- Folder used for locating source files for this project. If None, then the folder name is derived from 
    the call stack. For example, if this class' constructor is called in a file d:/users/me/csnMyProject.py, then d:/users/me 
    will be set as the source root folder.
    _compiler - The compiler (instance of csnCompiler.Compiler) that will be used for compiling this project. If set to None,
    then a new compiler instance will be created using csnBuild.globalCurrentCompilerType.
    """    
    def __init__(self, _name, _type, _sourceRootFolder = None, _compiler = None ):
        self.sources = []
        self.sourceGroups = dict()

        self.precompiledHeader = ""
        self.sourcesToBeMoced = []
        self.sourcesToBeUIed = []
        self.name = _name
        self.filesToInstall = dict()
        self.filesToInstall["Debug"] = dict()
        self.filesToInstall["Release"] = dict()
        self.type = _type
        self.rules = dict()
        self.customCommands = []
        
        if  _compiler is None:
            self.compiler = globalCurrentCompilerType()
        else:
            self.compiler = _compiler
        
        self.sourceRootFolder = _sourceRootFolder
        if self.sourceRootFolder is None:
            file = self.debug_call
            self.sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(file))
        self.useBefore = []
        if( self.type == "dll" ):
            self.buildSubFolder = "library/%s" % (_name)
        else:
            self.buildSubFolder = "%s/%s" % (self.type, _name)
        self.installSubFolder = ""
        self.configFilePath = "%s/%sConfig.cmake" % (self.buildSubFolder, _name)
        self.useFilePath = "%s/Use%s.cmake" % (self.buildSubFolder, _name)
        self.cmakeListsSubpath = "%s/CMakeLists.txt" % (self.buildSubFolder)
        self.projects = OrderedSet.OrderedSet()
        self.projectsNonRequired = OrderedSet.OrderedSet()
        self.generateWin32Header = 1

    def AddProjects(self, _projects, _dependency = 1): 
        """ 
        Adds projects in _projects as required projects. If an item in _projects is a function, then
        this function is called to retrieve the Project instance.
        _dependency - Flag that states that self target requires (is dependent on) _projects.
        Raises DependencyError in case of a cyclic dependency.
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
        _sourceGroup -- Place sources in this group (optional).
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
        Relative paths in _list are assumed to be relative to the third party binary folder.
        _debugOnly - If true, then the dll is only installed to the debug install folder.
        _releaseOnly - If true, then the dll is only installed to the release install folder.
        """
        
        if _location is None:
            _location = '.'
            
        for file in _list:
            if not _debugOnly:
                if not self.filesToInstall["Release"].has_key(_location):
                    self.filesToInstall["Release"][_location] = []
                if not file in self.filesToInstall["Release"][_location]:
                    self.filesToInstall["Release"][_location].append( file )
            if not _releaseOnly:
                if not self.filesToInstall["Debug"].has_key(_location):
                    self.filesToInstall["Debug"][_location] = []
                if not file in self.filesToInstall["Debug"][_location]:
                    self.filesToInstall["Debug"][_location].append( file )
                
    def AddDefinitions(self, _listOfDefinitions, _private = 0, _WIN32 = 0, _NOT_WIN32 = 0 ):
        """
        Adds definitions to self.compiler.
        _private -- Don't propagate these definitions to dependency projects.
        _WIN32 -- Only for Windows platforms.
        _NOT_WIN32 -- Only for non-Windows platforms.
        """
        if not self.compiler.IsForPlatform(_WIN32, _NOT_WIN32):
            return
        self.compiler.GetConfig(_private).definitions.extend(_listOfDefinitions)
        
    def AddIncludeFolders(self, _listOfIncludeFolders):
        """
        Adds items to self.publicIncludeFolders. 
        If an item has a relative path, then it will be prefixed with _sourceRootFolder.
        Added include paths must exist on the filesystem.
        If an item in _listOfIncludeFolders has wildcards, all matching folders will be added to the list.
        """
        for includeFolder in _listOfIncludeFolders:
            for folder in self.Glob(includeFolder):
                if (not os.path.exists(folder)) or os.path.isdir(folder):
                    self.compiler.public.includeFolders.append( folder )
        
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
        for libraryFolder in _listOfLibraryFolders:
            self.compiler.public.libraryFolders.append( self.__FindPath(libraryFolder) )
        
    def AddLibraries(self, _listOfLibraries, _WIN32 = 0, _NOT_WIN32 = 0, _debugOnly = 0, _releaseOnly = 0):
        """
        Adds items to self.publicLibraries. 
        _WIN32 -- Only for Windows platforms.
        _NOT_WIN32 -- Only for non-Windows platforms.
        _debug -- Only for the Debug configuration.
        _release  -- Only for the Release configuration.
        """
        if not self.compiler.IsForPlatform(_WIN32, _NOT_WIN32):
            return
            
        assert not( _debugOnly and _releaseOnly)
        type = "" # empty string is the default, meaning both debug and release
        if _debugOnly:
            type = "debug"
        if _releaseOnly:
            type = "optimized"

        for library in _listOfLibraries:
            self.compiler.public.libraries.append("%s %s" % (type, library))
        
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
            
        path = csnUtility.NormalizePath(path)
        return path
        
    def PrependSourceRootFolderToRelativePath(self, _path):
        """ 
        Returns _path prepended with self.sourceRootFolder, unless _path is already an absolute path (in that case, _path is returned).
        """
        path = csnUtility.NormalizePath(_path)
        if not os.path.isabs(path):
            path = os.path.abspath("%s/%s" % (self.sourceRootFolder, path))
        return csnUtility.NormalizePath(path)
    
    def Glob(self, _path):
        """ 
        Returns a list of files that match _path (which can be absolute, or relative to self.sourceRootFolder). 
        The return paths are absolute, containing only forward slashes.
        """
        return [csnUtility.NormalizePath(x) for x in glob.glob(self.PrependSourceRootFolderToRelativePath(_path))]
    
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
        for requiredProject in self.GetProjects(_onlyRequiredProjects = 1):
            if requiredProject in _skipList:
                continue
            if requiredProject is otherProject or requiredProject.DependsOn(otherProject, _skipList ):
                return 1
        return 0
        
    def GetProjects(self, _recursive = 0, _onlyRequiredProjects = 0, _skipList = None):
        """
        Returns list of all projects associated with this project.
        _recursive -- If true, returns not only child projects but all projects in the tree below this project.
        _onlyRequiredProjects -- If true, only projects that this project requires are returned.
        """
        result = OrderedSet.OrderedSet()
            
        if _onlyRequiredProjects:
            result.update(self.projects - self.projectsNonRequired)
        else:
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
                moreResults.update( project.GetProjects(_recursive, _onlyRequiredProjects, _skipList) )
            result.update(moreResults)
        return result
        
    def UseBefore(self, _otherProject):
        """ 
        Sets a flag that says that self must be used before _otherProjects in a cmake file. 
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
            
        for requiredProject in self.GetProjects(_recursive = 1, _onlyRequiredProjects = 1):
            if( otherProject in requiredProject.useBefore ):
                return 1
                
        return 0
           
    def ProjectsToUse(self):
        """
        Determine a list of projects that must be used (meaning: include the config and use file) to generate this project.
        Note that self is always the last project in this list.
        The list is sorted in the correct order, using Project.WantsToBeUsedBefore.
        """
        result = []
        
        projectsToUse = [project for project in self.GetProjects(_recursive = 1, _onlyRequiredProjects = 1)]
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
                    assert not otherProject is self, "Logical error. %s cannot be used before %s" % (self.name, project.name)
                    skipThisProjectForNow = 1
            if( skipThisProjectForNow ):
                projectsToUse.insert(0, project)
                continue
            else:
                result.append(project)
          
        result.remove(self)
        result.append(self)
        return result
        
    def GenerateConfigFile(self, _public):
        """
        Generates the XXXConfig.cmake file for this project.
        _public - If true, generates a config file that can be used in any cmake file. If false,
        it generates the private config file that is used in the csnake-generated cmake files.
        """
        fileConfig = self.GetPathToConfigFile(_public)
        f = open(fileConfig, 'w')
        
        # create list with folder where libraries should be found. Add the bin folder where all the
        # targets are placed to this list. 
        publicLibraryFolders = self.compiler.public.libraryFolders
        if _public:
            publicLibraryFolders.append(self.GetBinaryInstallFolder()) 

        # write header and some cmake fields
        f.write( "# File generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "SET( %s_FOUND \"TRUE\" )\n" % (self.name) )
        f.write( "SET( %s_USE_FILE \"%s\" )\n" % (self.name, self.GetPathToUseFile() ) )
        f.write( "SET( %s_INCLUDE_DIRS %s )\n" % (self.name, csnUtility.Join(self.compiler.public.includeFolders, _addQuotes = 1)) )
        f.write( "SET( %s_LIBRARY_DIRS %s )\n" % (self.name, csnUtility.Join(publicLibraryFolders, _addQuotes = 1)) )
        if( len(self.compiler.public.libraries) ):
            f.write( "SET( %s_LIBRARIES ${%s_LIBRARIES} %s )\n" % (self.name, self.name, csnUtility.Join(self.compiler.public.libraries, _addQuotes = 1)) )

        # add the target of this project to the list of libraries that should be linked
        if _public and len(self.sources) > 0 and (self.type == "library" or self.type == "dll"):
            targetName = self.name
            f.write( "SET( %s_LIBRARIES ${%s_LIBRARIES} %s )\n" % (self.name, self.name, csnUtility.Join([targetName], _addQuotes = 1)) )
                
    def GenerateUseFile(self):
        """
        Generates the UseXXX.cmake file for this project.
        """
        fileUse = "%s/%s" % (self.compiler.GetBuildFolder(), self.useFilePath)
        f = open(fileUse, 'w')
        
        # write header and some cmake fields
        f.write( "# File generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "INCLUDE_DIRECTORIES(${%s_INCLUDE_DIRS})\n" % (self.name) )
        f.write( "LINK_DIRECTORIES(${%s_LIBRARY_DIRS})\n" % (self.name) )
        
        # write definitions     
        if( len(self.compiler.public.definitions) ):
            f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(self.compiler.public.definitions) )
   
        # write definitions that state whether this is a static library
        #if self.type == "library":
        #    f.write( "ADD_DEFINITIONS(%sSTATIC)\n" % self.name )
            
    def GetPathToConfigFile(self, _public):
        """ 
        Returns self.useFilePath if it is absolute. Otherwise, returns self.compiler.GetBuildFolder() + self.useFilePath.
        If _public is false, and the project is not of type 'third party', then the postfix ".private" 
        is added to the return value.
        """
        if( os.path.isabs(self.configFilePath) ):
            result = self.configFilePath
        else:
            result = "%s/%s" % (self.compiler.GetBuildFolder(), self.configFilePath)

        postfix = ""
        if self.type in ("dll", "library", "executable") and (not _public):
            postfix = ".private"
             
        return result + postfix


    def GetPathToUseFile(self):
        """ 
        Returns self.useFilePath if it is absolute. Otherwise, returns self.compiler.GetBuildFolder() + self.useFilePath.
        """
        if( os.path.isabs(self.useFilePath) ):
            return self.useFilePath
        else:
            return "%s/%s" % (self.compiler.GetBuildFolder(), self.useFilePath)
        
    def ResolvePathsOfFilesToInstall(self, _thirdPartyBinFolder, _skipCVS = 1):
        """ 
        This function replaces relative paths and wildcards in self.filesToInstall with absolute paths without wildcards.
        Any folder is replaced by a complete list of the files in that folder.
        _skipCVS - If true, folders called CVS and .svn are automatically skipped. 
        """
        excludedFolderList = ("CVS", ".svn")
        for mode in ("Debug", "Release"):
            projects = self.GetProjects(_recursive = 1)
            projects.add(self)
            for project in projects:
                for location in project.filesToInstall[mode].keys():
                    newList = []
                    for dllPattern in project.filesToInstall[mode][location]:
                        path = csnUtility.NormalizePath(dllPattern)
                        if not os.path.isabs(path):
                            path = "%s/%s" % (_thirdPartyBinFolder, path)
                        for dll in glob.glob(path):
                            skip = (os.path.basename(dll) in excludedFolderList and _skipCVS and os.path.isdir(dll))
                            if not skip:
                                newList.append(dll)
                    
                    newListWithOnlyFiles = []
                    for file in newList:
                        if os.path.isdir(file):
                            for folderFile in GlobDirectoryWalker.Walker(file, ["*"], excludedFolderList):
                                if not os.path.isdir(folderFile):
                                    newListWithOnlyFiles.append(folderFile)
                        else:
							newListWithOnlyFiles.append(file)
                        
                    project.filesToInstall[mode][location] = newListWithOnlyFiles
    
    def SetGenerateWin32Header(self, _flag):
        """ If _flag, then the Win32Header is generated for this project. """
        self.generateWin32Header = _flag

    def GetGenerateWin32Header(self):
        """ See SetGenerateWin32Header """
        return self.generateWin32Header
                   
    def CreateCMakeSection_IncludeConfigAndUseFiles(self, f):
        """ Include the use file and config file for any dependency project, and finally also
        add the use and config file for this project (do this last, so that all definitions from
        the dependency projects are already included).
        """
        assert hasattr(self.compiler, "buildFolder"), "Project %s has no compiler with buildFolder\n" % self.name
        for project in self.ProjectsToUse():
            f.write( "\n# use %s\n" % (project.name) )
            f.write( "INCLUDE(\"%s\")\n" % (project.GetPathToConfigFile(_public = (self.name != project.name and not csnUtility.IsRunningOnWindows())) ))
            f.write( "INCLUDE(\"%s\")\n" % (project.GetPathToUseFile()) )
    
    def CreateCMakeSection_SourceGroups(self, f):
        """ Create source groups in the CMakeLists.txt """
        for groupName in self.sourceGroups:
            f.write( "\n # Create %s group \n" % groupName )
            f.write( "IF (WIN32)\n" )
            f.write( "  SOURCE_GROUP(\"%s\" FILES %s)\n" % (groupName, csnUtility.Join(self.sourceGroups[groupName], _addQuotes = 1)))
            f.write( "ENDIF(WIN32)\n\n" )
    
    def CreateCMakeSection_MocRules(self, f):
        """ Create moc rules in the CMakeLists.txt """
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
        """ Create uic rules in the CMakeLists.txt """
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
        """ Create definitions in the CMakeLists.txt """
        if( len(self.compiler.private.definitions) ):
            f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(self.compiler.private.definitions) )

    def CreateCMakeSection_Sources(self, f, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar):
        """ Add sources to the target in the CMakeLists.txt """
        sources = self.sources
        if len(sources) == 0:
            sources.append( csnUtility.GetDummyCppFilename() )
        if(self.type == "executable" ):
            f.write( "ADD_EXECUTABLE(%s %s %s %s %s)\n" % (self.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(sources, _addQuotes = 1)) )
            
        elif(self.type == "library" ):
            f.write( "ADD_LIBRARY(%s STATIC %s %s %s %s)\n" % (self.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(sources, _addQuotes = 1)) )
        
        elif(self.type == "dll" ):
            f.write( "ADD_LIBRARY(%s SHARED %s %s %s %s)\n" % (self.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(sources, _addQuotes = 1)) )
            
        else:
            raise NameError, "Unknown project type %s" % self.type
        
    def CreateCMakeSection_InstallRules(self, f, _installFolder):
        """ Create install rules in the CMakeLists.txt """
        if( _installFolder != "" and self.type != "library"):
            destination = "%s/%s" % (_installFolder, self.installSubFolder)
            f.write( "\n# Rule for installing files in location %s\n" % destination)
            f.write( "INSTALL(TARGETS %s DESTINATION %s)\n" % (self.name, destination) )
    
    def CreateCMakeSection_Rules(self, f):
        """ Create other rules in the CMakeLists.txt """
        for description, rule in self.rules.iteritems():
            f.write("\n#Adding rule %s\n" % description)
            f.write("ADD_CUSTOM_COMMAND( TARGET %s PRE_BUILD COMMAND %s WORKING_DIRECTORY \"%s\" COMMENT \"Running rule %s\" VERBATIM )\n" % (self.name, rule.command, rule.workingDirectory, description))
    
    def CreateCMakeSection_Link(self, f):
        """ Create link commands in the CMakeLists.txt """
        if self.type in ("dll", "executable"):
            targetLinkLibraries = ""
            for project in self.GetProjects(_recursive = 1, _onlyRequiredProjects = 1):
                if not project.type in ("dll", "library", "executable", "prebuilt"):
                    continue
                targetLinkLibraries = targetLinkLibraries + ("${%s_LIBRARIES} " % project.name) 
            f.write( "TARGET_LINK_LIBRARIES(%s %s)\n" % (self.name, targetLinkLibraries) )
        
    def CreateCMakeSections(self, f, _installFolder):
        """ Writes different CMake sections for this project to the file f. """
    
        self.CreateCMakeSection_IncludeConfigAndUseFiles(f)
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

    def CreateExtraSourceFilesForTesting(self):
        """ 
        Tests if this project is a test project. If so, checks if the test runner output file exists. If not, creates a dummy file.
        This dummy file is needed, for otherwise CMake will not include the test runner source file in the test project.
        """
        assert hasattr(self, "testRunnerSourceFile")
        testRunnerSourceFile = "%s/%s" % (self.GetBuildFolder(), self.testRunnerSourceFile)
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

    def AddCustomCommand(self, command):
        """ Adds command to the list of custom commands. Each command must accept this instance (self) as the one and only argument. """
        self.customCommands.append(command)

    def RunCustomCommands(self):
        """ Runs commands in self.customCommands, passing self as the one and only argument. """
        for command in self.customCommands:
            command(self)
            
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
        # when the test project is generated, the CreateExtraSourceFilesForTesting method must be executed
        self.testProject.AddCustomCommand(Project.CreateExtraSourceFilesForTesting)
        
        # todo: find out where python is located
        wxRunnerArg = ""
        if _enableWxWidgets:
            wxRunnerArg = "--template \"%s\"" % (csnUtility.GetRootOfCSnake() + "/TemplateSourceFiles/wxRunner.tpl")
        self.testProject.AddRule("Create test runner", "\"%s\" %s %s --have-eh --error-printer -o %s " % (csnUtility.NormalizePath(pythonPath), pythonScript, wxRunnerArg, self.testProject.testRunnerSourceFile))
        self.testProject.AddProjects([cxxTestProject, self])
        self.AddProjects([self.testProject], _dependency = 0)
        
    def AddTests(self, listOfTests, _cxxTestProject, _enableWxWidgets = 0):
        """
        _cxxTestProject -- May be the cxxTest project instance, or a function returning a cxxTest project instance.
        listOfTests -- List of source files containing cxx test classes.
        """
        cxxTestProject = ToProject(_cxxTestProject)
        
        if not hasattr(self, "testProject"):
            self.CreateTestProject(cxxTestProject, _enableWxWidgets)
            
        rule = self.testProject.rules["Create test runner"]
        for test in listOfTests:
            absPathToTest = self.PrependSourceRootFolderToRelativePath(test)
            rule.command += "\"%s\"" % absPathToTest
            self.testProject.AddSources([absPathToTest], _checkExists = 0)

    def GetBuildFolder(self):
        """
        Returns the bin folder for storing intermediate build files for this project.
        """
        return self.compiler.GetBuildFolder() + "/" + self.buildSubFolder

    def WriteDependencyStructureToXML(self, filename):
        """
        Writes an xml file containing the dependency structure for this project and its dependency projects.
        """
        f = open(filename, 'w')
        self.WriteDependencyStructureToXMLImp(f)
        f.close()

    def WriteDependencyStructureToXMLImp(self, f, indent = 0):
        """
        Helper function.
        """
        for i in range(indent):
            f.write(' ')
        f.write("<%s>" % self.name)
        for project in self.GetProjects(_onlyRequiredProjects = 1):
            project.WriteDependencyStructureToXMLImp(f, indent + 4)
        f.write("</%s>\n" % self.name)

    def GetBinaryInstallFolder(self, _configurationName = "${CMAKE_CFG_INTDIR}"):
        """ 
        Returns location in the binary folder where binaries for this project must be installed.
        This functions is used for being able to "install" all files in the binary folder that are needed to run the application
        from the binary folder without having to install to the Install Folder.
        """
        result = self.compiler.GetOutputFolder(_configurationName)
        if self.installSubFolder != "":
            if _configurationName == "DebugAndRelease":
                result += "/${CMAKE_CFG_INTDIR}"
            result += "/%s" % self.installSubFolder
        return result

    def GetCMakeListsFilename(self):
        """ Return the filename for the CMakeLists.txt file for this project. """
        return "%s/%s" % (self.compiler.GetBuildFolder(), self.cmakeListsSubpath)
