## @package csnAPIImplementation
# Private implementation of API functions for the communication between csnake files and csnake.
# ATTENTION: DON'T IMPORT THIS DIRECTLY FROM CSNAKE FILES!!!


import csnGenerator

import copy
from csnVersion import Version
from csnProject import GenericProject, ThirdPartyProject
import csnProject
from csnStandardModuleProject import StandardModuleProject
import os.path
import csnUtility
import types
import new


# *********************************************************************************************************************
# *                                              Maintenance of this API                                              *
# *********************************************************************************************************************
# 
# 
# Adding functionality:
# ---------------------
# 
# The new functionality should be available for everyone. But you should give a warning, if people want to use a
# functionality that did not exist in the version that the user specified because that means that the user didn't choose
# the adequate API version (his code would crash, if it was really used with the version that he specified).
# 
# Note: Once added a functionality to the API in a release, it is hard to remove it again. You never get really rid of
# it, see below section "Removing functionality". So before adding stuff to the API, let it go for a day or two and
# think it over again after that time. Does it really make sense to add this function? Doesn't it expose too much CSnake
# internals to the user? Will refactoring be equally simple after adding the function? Could the function possibly break
# stuff?
# 
# Implementation summary:
# - Older versions: Warning + Functionality (Add a method to API*Base that gives a warning and class (statically) the
#                   implementation in the subclass. Check if that static call is possible: The method of the subclass
#                   may rely on new class members that your base class doesn't have.)
# - Newer versions: Functionality (override the above defined new method in a new subclass and implement the
#                   functionality there)
# 
# 
# Changing functionality:
# -----------------------
# 
# If you want to change the behavior of a function, keep both versions of the functionality and execute one or the
# other depending on the API version. No warnings are necessary.
# 
# Implementation summary:
# - Older versions: Old Functionality (already implemented in old class versions, no need to touch it)
# - Newer versions: New Functionality (override method in a new subclass)
# 
# 
# Removing functionality:
# -----------------------
# 
# Normally you only want to remove functionality, if having the specified functionality breaks stuff, i.e. it's not an
# issue of the implementation, the problem exists because of the specified functionality itself, it cannot be fixed by
# changing its implementation. Unfortunately, for the sake of backwards compatibility, in old API versions you still
# need to keep the functionality and maintain it (so watch out when adding stuff, you won't get rid of it afterwards!).
# As you normally only remove functionality in severe cases, you should both give a warning in older API versions (the
# user should stop using the functionality, if he has the possibility to do so) and throw an exception, if people try
# to use the function in newer versions (so in those versions it's actually removed).
# 
# Implementation summary:
# - Older versions: Functionality + Warning (add the warning to the method implementation in all old versions)
# - Newer versions: Exception (override method in a new subclass: throw exception)
# 
# 
# Adapting the API to changes in the CSnake core:
# -----------------------------------------------
# 
# Adapt (all versions of) the API implementation so that the functionality (seen from the point of view of the CSnake
# file) in every version of the API stays the same as before the change.
# 
# 
# General Hints:
# --------------
# 
# - Extend/modify/remove functionality creating new subclasses of the latest versions of the classes.
# - Only modify older versions of classes, if that is necessary to keep its original functionality (see "Adapting the
#   API to changes [...]") or to add a warning, if a function will be removed in future API versions (and is therefore
#   probably harmful).
# - Avoid calling public (and therefore in C++ terminology "virtual") functions, they will likely be overridden in the
#   future, so you can't rely on their exact behavior.
# - Within this module it is allowed to access private members of other (unrelated) and superclasses. This avoids the
#   before mentioned (bad) call of "virtual" functions and avoids exposing internal details to the CSnake file
# 


def _UnwrapProject(project):
    """ Unwrap a project from an input method or api project to a GenericProject. """
    if type(project) == types.FunctionType:
        project = project()
    if isinstance(project, _APIVeryGenericProject_Base):
        project = project._APIVeryGenericProject_Base__project
    return project

def _UnwrapProjectAndCustomMemberFunctions(project):
    """ Unwrap a project from an input method or api project to a GenericProject and return its custom member functions. """
    if type(project) == types.FunctionType:
        project = project()
    customMemberFunctions = None
    if isinstance(project, _APIVeryGenericProject_Base):
        customMemberFunctions = project._APIVeryGenericProject_Base__customMemberFunctions
        project = project._APIVeryGenericProject_Base__project
    return (customMemberFunctions, project)


######################
# VeryGenericProject #
######################

class _APIVeryGenericProject_Base:
    
    def __init__(self, project, apiVersion):
        # Note: As the class _APIStandardModuleProject_2_5_0 uses multiple inheritance and derives in two ways from this
        # class, it is possible that this constructor is called two times. This wouldn't hurt in its current
        # implementation. If you plan to change this constructor, make sure it won't hurt after your change, either.
        self.__project = project
        self.__apiVersion = apiVersion
        self.__customMemberFunctions = dict()
    
    def GetName(self):
        """ Returns the project name defined when creating the project. """
        return self.__project.name

    def AddProjects(self, projects, dependency = True, includeInSolution = True):
        """
        Connect other projects to this project. The semantics of this operations depends of the parameters "dependency" and "includeInSolution".
        projects   - List of projects to connect.
        dependency - If true, then the projects in the list "projects" are dependency of the reference project. The public
                     include folders of the projects in "projects" are added to the include paths of the reference project.
                     The reference project is linked against the libraries created by the projects in "projects".
                     If false, then none of the before-mentioned happens, but instead the projects in "projects" will
                     appear in the "Select Projects" tab of the GUI as suggestions, whenever the reference project is to
                     be compiled. The user can then decide, if he wants to compile those additional, suggested projects, too.
        includeInSolution - Determines, if the projects in "projects" will appear in the solution, so the user can easily
                            edit source files of those projects. If false, the projects will still be compiled, but won't
                            appear in the solution.
        """
        # unwrap the input projects before adding them
        unwrapped = map(_UnwrapProject, projects)
        # GenericProject.AddProjects only wants GenericProjects
        self.__project.AddProjects(unwrapped, dependency, includeInSolution)
    
    def GetBuildFolder(self):
        """ Returns the build folder, where the compile configuration and intermediate files of this project's compilation are stored. """
        return self.__project.GetBuildFolder()

    def AddFilesToInstall(self, filesToInstall, location = None, debugOnly = 0, releaseOnly = 0):
        """
        Registers files to be copied when doing "Install files to build folder". "debugOnly" and "releaseOnly" cannot
        be True at the same time.
        filesToInstall - A list of files to be copied
        location       - Folder to copy the files to
        debugOnly      - if True, the file is copied only to the configuration in Debug mode
        releaseOnly    - if True, the file is copied only to the configuration in Release mode
        """
        self.__project.AddFilesToInstall(filesToInstall, location, debugOnly, releaseOnly, True, True)
    
    def Glob(self, path):
        """
        Returns a list of files/directories matching the wildcard expression given by "path".
        path - Wildcard expression determining the result files (relativ to the project source directory)
        """
        return self.__project.Glob(path)
    
    def AddCustomMemberFunction(self, name, function):
        """
        Add a member function to the project object. The function will also be maintained, if the project object is
        rewrapped to another API version (then it is copied to the new wrapper, too). In the case of rewrapping the
        API version of the "self" object will always be the original one.
        Example usage: After doing "project.AddCustomMemberFunction("myCustomFunc", testFunc)" you will be able to call
        "testFunc" like this: "project.testFunc(...)"
        name     - Name of the member function (the function will be called using this name)
        function - Function to be added as member function (has to have at least one parameter: the project)
        """
        # Bind the function to this object
        function = new.instancemethod(function, self)
        # Add it to object
        self.__dict__[name] = function
        # Remember the bound function (in order to transfer it to a rewrapped project, if necessary)
        self.__customMemberFunctions[name] = function
    
    def GetProjects(self, recursive = False, onlyRequiredProjects = False, includeSelf = False, applyFilter = True):
        """
        Get the dependencies of this project in a sorted array (dependencies before dependents).
        recursive - If True, all (including indirectly) connected projects are returned; if False, only the directly
                    connected projects are returned.
        onlyRequiredProjects - If True, only the required projects (that the reference project depends on) are returned;
                               if False, all connected projects (including "suggestions") are returned.
        includeSelf - If True, the reference project is included in the result list, otherwise not.
        applyFilter - If True, the project filter ("Select Projects" tab in the GUI) is applied, so connections to
                      deactivated projects (and therefore also transitive connections) are removed; if False, all
                      connected projects are returned, independently of their activation state.
        """
        projects = self.__project.dependenciesManager.GetProjects(_recursive = recursive,
            _onlyRequiredProjects = onlyRequiredProjects,
            _includeSelf = includeSelf,
            _onlyPublicDependencies = False,
            _onlyNonRequiredProjects = False,
            _filter = applyFilter)
        api = FindAPI(self.__apiVersion)
        return map(api.RewrapProject, projects)
    

##################
# GenericProject #
##################

class _APIGenericProject_Base(_APIVeryGenericProject_Base):
    
    def __init__(self, project, apiVersion):
        # Note: As the sub class uses multiple inheritance and derives in two ways from this
        # class, it is possible that this constructor is called two times. This wouldn't hurt in its current
        # implementation. If you plan to change this constructor, make sure it won't hurt after your change, either.
        _APIVeryGenericProject_Base.__init__(self, project, apiVersion)
        self.__project = project
        self.__apiVersion = apiVersion
    
    def AddSources(self, sources, sourceGroup = "", checkExists = 1, forceAdd = 0):
        """
        Adds source files to the project that will be compiled.
        sources     - List of source files
        sourceGroup - Name of the Visual Studio project sub folder (overrides default source/header folder if non-empty)
        checkExists - Check if the files really exist before adding them (throws an exception, if they don't exist)
        forceAdd    - Force the addition of the files even if they do not exist (needs 'checkExists' to be set to false).
        """
        self.__project.AddSources(sources, False, False, sourceGroup, checkExists, forceAdd)
        
    def GetSources(self):
        """
        Returns a list of source files compiled by this project. Don't call this, if not absolutely necessary,
        this will substantially slow down the loading of CSnake instances.
        """
        return self.__project.GetSources()
        
    def SetPrecompiledHeader(self, precompiledHeader):
        """ Sets the filename of the precompiled header for the project. """
        self.__project.SetPrecompiledHeader(precompiledHeader)
    
    def AddIncludeFolders(self, includeFolders):
        """ Adds an include folder to the project. """
        self.__project.AddIncludeFolders(includeFolders, True, True)
    
    def AddProperties(self, properties):
        """
        A list of custom properties for the target that will be added using the CMake macro ADD_PROPERTY
        properties - A list of properties in the format of the macro ADD_PROPERTY
        """
        self.__project.AddProperties(properties)
    
    def AddDefinitions(self, listOfDefinitions, private = 0):
        """
        Adds a list of definitions to the project.
        listOfDefinitions - A list of the definitions to add to the project in the format of the CMake macro ADD_DEFINITIONS
        """
        self.__project.AddDefinitions(listOfDefinitions, private, True, True)

    def AddLibraries(self, libraries, debugOnly = 0, releaseOnly = 0):
        """
        Adds additional external libraries that this project has to link against; debugOnly and releaseOnly are not
        allowed to be True at the same time.
        debugOnly   - if True, only the debug version of the project is linked against the given libraries
        releaseOnly - if True, only the release version of the project is linked against the given libraries
        """
        self.__project.AddLibraries(libraries, True, True, debugOnly, releaseOnly)
    
    def AddTests(self, tests, cxxTestProject, enableWxWidgets = 0, dependencies = None, pch = ""):
        """
        Add tests to the project.
        tests - List of source files containing cxx test classes
        cxxTestProject - Project representing the CXXTEST thirdparty library
        enableWxWidgets - Enable wxWidgets in the tests.
        """
        testProject = _UnwrapProject(cxxTestProject)
        self.__project.AddTests(tests, testProject, enableWxWidgets, dependencies, pch)
    
    def GetTestProject(self):
        """ Returns the project that compiles all automatic tests for this project, so the user can modify its properties, if necessary. """
        testProject = self.__project.testProject
        if testProject:
            return _FindAPIGenericProjectConstructor(self.__apiVersion)(testProject, self.__apiVersion)
        else:
            raise APIError("No test present!")
    
    def GenerateWin32Header(self, generate = True):
        """ Determines, if a header file with import/export definitions for Windows DLLs has to be generated. """
        self.__project.SetGenerateWin32Header(generate)
    
    def AddCustomCommand(self, command):
        """
        Registers a function that will be executed when configuring this project.
        command - The callback function that is executed, when the reference project is configured
        """
        self.__project.AddCustomCommand(command)
    
    def CreateHeader(self, filename = None, variables = None, variablePrefix = None):
        """
        Creates a configuration header file in the build directory of the project, where it can be found by the
        project itself and dependent projects.
        filename - file name of the header file
        variables - map of variable names (string) to values (string) that are defined as C preprocessor defines in
                    the header file; in addition to the variables given here the source and build folders of the
                    reference project are defined
        variablePrefix - prefix for the variable names given in the parameter "variables" to avoid name conflicts; if
                         none is given then the project name (modified to be suitable as C preprocessor variable name)
                         is used as prefix
        """
        self.__project.CreateHeader(filename, variables, variablePrefix)
    
    def AddCMakeInsertBeforeTarget(self, callback, parameters = {}):
        """
        Registers a callback function that is called when writing the project's CMakeLists.txt and that can return
        a text as string that is included in the CMakeLists.txt before this project's target.
        callback   - callback function to be called when writing the CMakeLists.txt
        parameters - optional set of parameters to pass to the callback function (map: parameter-name -> value); in
                     addition to them the reference project is given to the callback function as first parameter, wrapped
                     with the API version with that this function was called
        """
        self.__project.AddCMakeInsertBeforeTarget(callback, self, parameters)
    
    def AddCMakeInsertAfterTarget(self, callback, parameters = {}):
        """
        Registers a callback function that is called when writing the project's CMakeLists.txt and that can return
        a text as string that is included in the CMakeLists.txt after this project's target.
        callback   - callback function to be called when writing the CMakeLists.txt
        parameters - optional set of parameters to pass to the callback function (map: parameter-name -> value); in
                     addition to them the reference project is given to the callback function as first parameter, wrapped
                     with the API version with that this function was called
        """
        self.__project.AddCMakeInsertAfterTarget(callback, self, parameters)
    
    def AddPostCMakeTasks(self, tasks):
        """
        Registers a list of functions that will be executed after executing CMake.
        tasks - A list of callback functions that will be executed after executing CMake. The first parameter of this
                function call will be the reference project (wrapped in the same API version as when calling this
                function), the second one an object that can be used to ask question to the user.
        """
        tasksWithWrappedProject=[]
        for task in tasks:
            tasksWithWrappedProject.append(lambda _, askUser : task(self, askUser))
        self.__project.AddPostCMakeTasks(tasksWithWrappedProject)
    
    def GetBuildResultsFolder(self, configurationName):
        """
        Returns the directory in which the resulting library/application (whatever the linking result is) will be created
        configurationName - "Debug" or "Release"
        """
        if configurationName:
            return self.__project.GetBuildResultsFolder(configurationName)
        else:
            return self.__project.GetBuildResultsFolder()
    

class _APIGenericProject_2_5_0(_APIGenericProject_Base):
    
    def __init__(self, project, apiVersion):
        _APIGenericProject_Base.__init__(self, project, apiVersion)
        self.__project = project


#########################
# StandardModuleProject #
#########################

class _APIStandardModuleProject_Base(_APIGenericProject_Base):
    
    def __init__(self, project, apiVersion):
        _APIGenericProject_Base.__init__(self, project, apiVersion)
        self.__project = project
    
    def AddApplications(self, modules, pch = "", applicationDependenciesList = None, holderName = None, properties = []):
        """
        Creates extra CSnake projects, each project building one application in the 'Applications' subfolder of the
        current project.
        modules - List of the subfolders within the 'Applications' subfolder that must be scanned for applications
        pch - If not "", this is the include file used to generate a precompiled header for each application
        applicationDependenciesList - List of dependencies for the applications that are not yet covered by the
                                      dependencies of the library itself
        holderName - Applications' name prefix.
        properties - A list of properties in the format of the macro ADD_PROPERTY for the application projects.
        """
        self.__project.AddApplications(modules, pch, applicationDependenciesList, holderName, properties)

    def AddLibraryModules(self, modules):
        """
        Adds source files and public include folders to the project, using a set of libmodules. It is assumed that the
        root folder of self has a subfolder called libmodules. The subfolders of libmodules should contain a subfolder
        called src (e.g. for mymodule, this would be libmodules/mymodule/src). If the src folder has a subfolder called
        'stub', it is also added to the source tree.
        modules - A list of subfolders of the libmodules folder that should be added to the project.
        """
        self.__project.AddLibraryModules(modules)
    
    
class _APIStandardModuleProject_2_5_0(_APIStandardModuleProject_Base, _APIGenericProject_2_5_0):
    
    def __init__(self, project, apiVersion):
        _APIStandardModuleProject_Base.__init__(self, project, apiVersion)
        self.__project = project


#########################
#   ThirdPartyProject   #
#########################

class _APIThirdPartyProject_Base(_APIVeryGenericProject_Base):
    
    def __init__(self, project, apiVersion):
        _APIVeryGenericProject_Base.__init__(self, project, apiVersion)
        self.__project = project
    
    def SetUseFilePath(self, path):
        """
        Sets the path to the CMake-style use-file of this third party project. The file has to be created by the
        project's "CMakeLists.txt" during configuration of the third party folders.
        """
        self.__project.SetUseFilePath(path)

    def SetConfigFilePath(self, path):
        """
        Sets the path to the CMake-style config-file of this third party project. The file has to be created by the
        project's "CMakeLists.txt" during configuration of the third party folders.
        """
        self.__project.SetConfigFilePath(path)
    

class _APIThirdPartyProject_2_5_0(_APIThirdPartyProject_Base):
    
    def __init__(self, project, apiVersion):
        _APIThirdPartyProject_Base.__init__(self, project, apiVersion)
        self.__project = project


##################
#    Compiler    #
##################

class _APICompiler_Base:
    
    def __init__(self, compiler):
        self.__compiler = compiler
    
    def GetName(self):
        """ Returns the name of the build system (e.g. "Unix Makefiles", "Visual Studio 7 .NET 2003") in CMake style. """
        return self.__compiler.GetName()
    
    def TargetIsWindows(self):
        """ Returns true, if the compilation target is a Windows platform, false if not. """
        return self.__compiler.IsForPlatform(_WIN32 = True, _NOT_WIN32 = False)
    
    def TargetIsUnix(self):
        """ Returns true, if the compilation target is a Unix-like platform (e.g. Linux, MacOSX), false if not. """
        return self.__compiler.IsForPlatform(_WIN32 = False, _NOT_WIN32 = True)

    def TargetIsLinux(self):
        """ Returns true, if the compilation target is a Linux platform, false if not. """
        return self.__compiler.TargetIsLinux()
    
    def TargetIsMac(self):
        """ Returns true, if the compilation target is a Mac platform, false if not. """
        return self.__compiler.TargetIsMac()
    
    def TargetIs32Bits(self):
        """ Returns true, if the compilation target is a 32 Bit platform, false if not. """
        return self.__compiler.TargetIs32Bits()
    
    def TargetIs64Bits(self):
        """ Returns true, if the compilation target is a 64 Bit platform, false if not. """
        return self.__compiler.TargetIs64Bits()
    

class _APICompiler_2_5_0(_APICompiler_Base):
    
    def __init__(self, compiler):
        _APICompiler_Base.__init__(self, compiler)
        self.__compiler = compiler


#############
#  Version  #
#############

class _APIVersion_Base:
    
    def __init__(self, version):
        self.__version = version
        
    def GetString(self, numDecimals):
        """
        Returns the given version number as String in the format "1.13.7-beta".
        numDecimals - Determines the minimum of numbers to be displayed behind the first dot. Non-zero numbers are
                      always displayed, independently of the parameter given.
        """
        return self.__version.GetString(numDecimals) 
    
    def __cmp__(self, other):
        """
        Compares the version number represented by the reference object with the version number in "other" and returns
        0, if they are equal; a negative number, if "other" is greater than the reference object; a positive number,
        if the reference object is greater than "other".
        """
        return self.__version.__cmp__(other.__version)


class _APIVersion_2_5_0(_APIVersion_Base):
    
    def __init__(self, version):
        _APIVersion_Base.__init__(self, version)


_currentCSnakeVersion = Version(csnGenerator.version)


#############
#    API    #
#############

class _API_Base:
    
    def __init__(self, version):
        self.__version = version
        self.__genericProjectConstructor = _FindAPIGenericProjectConstructor(version)
        self.__standardModuleProjectConstructor = _FindAPIStandardModuleProjectConstructor(version)
        self.__thirdPartyProjectConstructor = _FindAPIThirdPartyProjectConstructor(version)
        self.__compilerConstructor = _FindAPICompilerConstructor(version)
        self.__compiler = None
        self.__versionConstructor = _FindAPIVersionConstructor(version)
    
    def CreateCompiledProject(self, name, projectType, sourceRootFolder = None, categories = None, showInProjectTree = False):
        """
        Creates a compiled project.
        name - Project name
        projectType - Type of the project: Can be "executable", "library" or "dll".
        sourceRootFolder - The main folder of the library (many subsequent operations take subdirectory parameters relative
                           to this directory); if None, the location of the CSnake file calling this function is used.
        categories - Hierarchy of categories for the project tree of the "Select Projects" tab
        showInProjectTree - If True, the project will be shown in the project tree of the "Select Projects" tab (if there
                            is a connection between the selected instance and this project) and can be deselected (if the
                            selected instance doesn't depend on this project). If False, the project is always compiled, if
                            there is a connection between the selected instance and this project.
        """
        if sourceRootFolder is None:
            filename = csnProject.FindFilename(1)
            dirname = os.path.dirname(filename)
            sourceRootFolder = csnUtility.NormalizePath(dirname, _correctCase = False)
        if categories:
            showInProjectTree = True
        project = GenericProject(name, projectType, sourceRootFolder, [name] if showInProjectTree else None, _context=csnProject.globalCurrentContext)
        if categories:
            superCategory = " / ".join(categories)
            project.context.SetSuperSubCategory(superCategory, name)
        return self.__genericProjectConstructor(project, self.__version)

    def CreateStandardModuleProject(self, name, projectType, sourceRootFolder = None, categories = None, showInProjectTree = False):
        """
        Creates a compiled project (see "CreateCompiledProject") with the additional modules "AddApplications" and "AddLibraryModules".
        """
        if sourceRootFolder is None:
            filename = csnProject.FindFilename(1)
            dirname = os.path.dirname(filename)
            sourceRootFolder = csnUtility.NormalizePath(dirname, _correctCase = False)
        if categories:
            showInProjectTree = True
        project = StandardModuleProject(name, projectType, sourceRootFolder, [name] if showInProjectTree else None)
        if categories:
            superCategory = " / ".join(categories)
            project.context.SetSuperSubCategory(superCategory, name)
        return self.__standardModuleProjectConstructor(project, self.__version)

    def CreateThirdPartyProject(self, name, sourceRootFolder = None):
        """
        Creates a new third party project (project that has its source in one of the third party source folders
        and that is compiled using a custom "CMakeLists.txt" file rather than CSnake files. The CSnake project returned
        by this function can then be used to point dependent projects to the config- and use-file of this third party
        project, so other projects are able to use the libraries.
        """
        if sourceRootFolder is None:
            filename = csnProject.FindFilename(1)
            dirname = os.path.dirname(filename)
            sourceRootFolder = csnUtility.NormalizePath(dirname, _correctCase = False)
        project = ThirdPartyProject(name, csnProject.globalCurrentContext, sourceRootFolder)
        return self.__thirdPartyProjectConstructor(project, self.__version)
    
    def RewrapProject(self, project):
        """
        Returns a new object containing the same project, but with functions of the referenced API version
        (instead of the API version that the project was created with).
        """
        # Remove the old wrapper
        (customMemberFunctions, project) = _UnwrapProjectAndCustomMemberFunctions(project)
        # Add a new wrapper (depending on the project type)
        if isinstance(project, GenericProject):
            project = self.__genericProjectConstructor(project, self.__version)
        elif isinstance(project, StandardModuleProject):
            project = self.__standardModuleProjectConstructor(project, self.__version)
        elif isinstance(project, ThirdPartyProject):
            project = self.__thirdPartyProjectConstructor(project, self.__version)
        else:
            raise APIError("Unknown project type: %s" % str(type(project)))
        # Add the custom member functions to the new wrapper
        if not (customMemberFunctions is None):
            for name, function in customMemberFunctions:
                # Note: No need to bind the function to the new project wrapper - it's better to pass the object using a
                #       wrapper of the API version with which the project was created
                project.__dict__[name] = function
            project._APIVeryGenericProject_Base__customMemberFunctions = copy.copy(customMemberFunctions)
        return project
    
    def CreateVersion(self, version):
        """ Create a version object from a String or Array in order to safely compare version numbers. """
        return self.__versionConstructor(Version(version))
    
    def GetCSnakeVersion(self):
        """ Returns the version number of the CSnake version used. """
        return copy.copy(_currentCSnakeVersion)
    
    def GetChosenAPIVersion(self):
        """ Returns the version number of the API used. """
        return copy.copy(self.__version)
    
    def LoadThirdPartyModule(self, subFolder, name):
        """
        Imports the CSnake file of a third party project.
        subFolder - Where to find the CSnake file, given relative to one of the third party source folders
        name - Name of the CSnake file (without .py) to load from the folder given above
        """
        return csnProject.LoadThirdPartyModule(subFolder, name)
    
    def GetCompiler(self):
        """ Returns an object containing information about the build system, compiler and target platform. """
        if not self.__compiler:
            self.__compiler = self.__compilerConstructor(csnProject.globalCurrentContext.GetCompiler())
        return self.__compiler
    
    def GetDummyCppFilename(self):
        """ Returns the filename of an empty cpp file. """
        return csnUtility.GetDummyCppFilename()
    
    def FindScriptFilename(self, level = 0):
        """
        Find the filename of the source code that is (directly or indirectly) calling this function.
        level - 0: Find filename of the script calling FindScriptFilename (default),
                1: Find filename of the script calling the function that calls FindScriptFilename,
                x: Find filename of the script calling FindScriptFilename indirectly through x+1 function calls
        """
        return csnProject.FindFilename(1+level)
    
    def FindSourceRootFolder(self, level = 0):
        """
        Find the folder containing the CSnake file that is (directly or indirectly) calling this function.
        level - see function FindScriptFilename
        """
        return csnUtility.NormalizePath(os.path.dirname(csnProject.FindFilename(1+level)))
    

class _API_2_5_0(_API_Base):
    
    def __init__(self, version):
        _API_Base.__init__(self, version)


######################
# Constructor Caches #
######################
# In order to not have to search and/or instantiate the same class over and over again, we maintain caches


# API objects

_apiRegister = dict()

class APIError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def FindAPI(version):
    if not isinstance(version, Version):
        version = Version(version)
    if not version in _apiRegister:
        if version > _currentCSnakeVersion:
            raise APIError("Your CSnake version is too old to compile this code! Demanded API version: %s - CSnake version: %s"
                % (version.GetString(), _currentCSnakeVersion.GetString()))
        elif version >= Version([2, 5, 0, "beta"]):
            _apiRegister[version] = _API_2_5_0(version)
        else:
            # there was no API before this
            raise APIError("Unknown API version: %s" % version.GetString())
    return _apiRegister[version]


# GenericProject wrapper constructors

_apiGenericProjectConstructorRegister = dict()

def _FindAPIGenericProjectConstructor(version):
    if not version in _apiGenericProjectConstructorRegister:
        if version > _currentCSnakeVersion:
            raise APIError("Your CSnake version is too old to compile this code!")
        elif version >= Version([2, 5, 0, "beta"]):
            _apiGenericProjectConstructorRegister[version] = _APIGenericProject_2_5_0
        else:
            # there was no API before this
            raise APIError("Unknown API version")
    return _apiGenericProjectConstructorRegister[version]


# StandardModuleProject wrapper constructors

_apiStandardModuleProjectConstructorRegister = dict()

def _FindAPIStandardModuleProjectConstructor(version):
    if not version in _apiStandardModuleProjectConstructorRegister:
        if version > _currentCSnakeVersion:
            raise APIError("Your CSnake version is too old to compile this code!")
        elif version >= Version([2, 5, 0, "beta"]):
            _apiStandardModuleProjectConstructorRegister[version] = _APIStandardModuleProject_2_5_0
        else:
            # there was no API before this
            raise APIError("Unknown API version")
    return _apiStandardModuleProjectConstructorRegister[version]


# ThirdPartyProject wrapper constructors

_apiThirdPartyProjectConstructorRegister = dict()

def _FindAPIThirdPartyProjectConstructor(version):
    if not version in _apiThirdPartyProjectConstructorRegister:
        if version > _currentCSnakeVersion:
            raise APIError("Your CSnake version is too old to compile this code!")
        elif version >= Version([2, 5, 0, "beta"]):
            _apiThirdPartyProjectConstructorRegister[version] = _APIThirdPartyProject_2_5_0
        else:
            # there was no API before this
            raise APIError("Unknown API version")
    return _apiThirdPartyProjectConstructorRegister[version]


# Version class constructors

_apiVersionConstructorRegister = dict()

def _FindAPIVersionConstructor(version):
    if not version in _apiVersionConstructorRegister:
        if version > _currentCSnakeVersion:
            raise APIError("Your CSnake version is too old to compile this code!")
        elif version >= Version([2, 5, 0, "beta"]):
            _apiVersionConstructorRegister[version] = _APIVersion_2_5_0
        else:
            # there was no API before this
            raise APIError("Unknown API version")
    return _apiVersionConstructorRegister[version]


# Compiler wrapper constructors

_apiCompilerConstructorRegister = dict()

def _FindAPICompilerConstructor(version):
    if not version in _apiCompilerConstructorRegister:
        if version > _currentCSnakeVersion:
            raise APIError("Your CSnake version is too old to compile this code!")
        elif version >= Version([2, 5, 0, "beta"]):
            _apiCompilerConstructorRegister[version] = _APICompiler_2_5_0
        else:
            # there was no API before this
            raise APIError("Unknown API version")
    return _apiCompilerConstructorRegister[version]

