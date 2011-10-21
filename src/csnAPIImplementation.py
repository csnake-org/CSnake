## @package csnAPIImplementation
# Private implementation of API functions for the communication between csnake files and csnake.
# ATTENTION: DON'T IMPORT THIS DIRECTLY FROM CSNAKE FILES!!!


import csnGenerator

import copy
import re
from csnVersion import Version
from csnProject import GenericProject, ThirdPartyProject
import csnProject
from csnStandardModuleProject import StandardModuleProject
import os.path
import csnUtility
import types


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
# If you want to change the behaviour of a function, keep both versions of the functionality and execute one or the
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
#   future, so you can't rely on their exact behaviour.
# - Within this module it is allowed to access private members of other (unrelated) and superclasses. This avoids the
#   before mentioned (bad) call of "virtual" functions and avoids exposing internal details to the CSnake file
# 


def _UnwrapProject(project):
    """ Unwrap a project from an input method or api project to a GenericProject. """
    if type(project) == types.FunctionType:
        project = project()
    if isinstance(project, _APIVeryGenericProject_Base):
        # Funny line
        project = project._APIVeryGenericProject_Base__project
    return project


######################
# VeryGenericProject #
######################

class _APIVeryGenericProject_Base:
    
    def __init__(self, project):
        # Note: As the class _APIStandardModuleProject_2_4_5 uses multiple inheritance and derives in two ways from this
        # class, it is possible that this constructor is called two times. This wouldn't hurt in its current
        # implementation. If you plan to change this constructor, make sure it won't hurt after your change, either.
        self.__project = project

    def AddProjects(self, projects, dependency = True, includeInSolution = True):
        # unwrap the input projects before adding them
        unwrapped = map(_UnwrapProject, projects)
        # GenericProject.AddProjects only wants GenericProjects
        self.__project.AddProjects(unwrapped, dependency, includeInSolution)
    
    def GetBuildFolder(self):
        return self.__project.GetBuildFolder()

    def AddFilesToInstall(self, filesToInstall, location = None, debugOnly = 0, releaseOnly = 0, WIN32 = 0, NOT_WIN32 = 0):
        self.__project.AddFilesToInstall(filesToInstall, location, debugOnly, releaseOnly, WIN32, NOT_WIN32)
    
    def Glob(self, path):
        return self.__project.Glob(path)
    

##################
# GenericProject #
##################

class _APIGenericProject_Base(_APIVeryGenericProject_Base):
    
    def __init__(self, project):
        # Note: As the sub class uses multiple inheritance and derives in two ways from this
        # class, it is possible that this constructor is called two times. This wouldn't hurt in its current
        # implementation. If you plan to change this constructor, make sure it won't hurt after your change, either.
        _APIVeryGenericProject_Base.__init__(self, project)
        self.__project = project
    
    def AddSources(self, sources, moc = 0, ui = 0, sourceGroup = "", checkExists = 1, forceAdd = 0):
        self.__project.AddSources(sources, moc, ui, sourceGroup, checkExists, forceAdd)
        
    def SetPrecompiledHeader(self, precompiledHeader):
        self.__project.SetPrecompiledHeader(precompiledHeader)
    
    def AddIncludeFolders(self, includeFolders, WIN32 = 0, NOT_WIN32 = 0):
        self.__project.AddIncludeFolders(includeFolders, WIN32, NOT_WIN32)
    
    def AddProperties(self, properties):
        self.__project.AddProperties(properties)
    
    def AddDefinitions(self, listOfDefinitions, private = 0, WIN32 = 0, NOT_WIN32 = 0):
        self.__project.AddDefinitions(listOfDefinitions, private, WIN32, NOT_WIN32)

    def AddLibraries(self, libraries, WIN32 = 0, NOT_WIN32 = 0, debugOnly = 0, releaseOnly = 0):
        self.__project.AddLibraries(libraries, WIN32, NOT_WIN32, debugOnly, releaseOnly)
    
    def AddTests(self, tests, cxxTestProject, enableWxWidgets = 0, dependencies = None, pch = ""):
        testProject = _UnwrapProject(cxxTestProject)
        self.__project.AddTests(tests, testProject, enableWxWidgets, dependencies, pch)
    
    def AddSourceToTest(self):
        # TODO
        pass
    
    def GenerateWin32Header(self, generate = True):
        self.__project.SetGenerateWin32Header(generate)
    
    def AddCustomCommand(self, command):
        self.__project.AddCustomCommand(command)
    
    def CreateHeader(self, filename = None, variables = None, variablePrefix = None):
        self.__project.CreateHeader(filename, variables, variablePrefix)
    
    def AddCMakeInsertBeforeTarget(self, callback, parameters = {}):
        self.__project.AddCMakeInsertBeforeTarget(callback, self, parameters)
    
    def AddCMakeInsertAfterTarget(self, callback, parameters = {}):
        self.__project.AddCMakeInsertAfterTarget(callback, self, parameters)
        
class _APIGenericProject_2_4_5(_APIGenericProject_Base):
    
    def __init__(self, project):
        _APIGenericProject_Base.__init__(self, project)
        self.__project = project


#########################
# StandardModuleProject #
#########################

class _APIStandardModuleProject_Base(_APIGenericProject_Base):
    
    def __init__(self, project):
        _APIGenericProject_Base.__init__(self, project)
        self.__project = project
    
    def AddApplications(self, modules, pch = "", applicationDependenciesList = None, holderName = None, properties = []):
        self.__project.AddApplications(modules, pch, applicationDependenciesList, holderName, properties)

    def AddLibraryModules(self, modules):
        self.__project.AddLibraryModules(modules)
    
    
class _APIStandardModuleProject_2_4_5(_APIStandardModuleProject_Base, _APIGenericProject_2_4_5):
    
    def __init__(self, project):
        _APIStandardModuleProject_Base.__init__(self, project)
        self.__project = project


#########################
#   ThirdPartyProject   #
#########################

class _APIThirdPartyProject_Base(_APIVeryGenericProject_Base):
    
    def __init__(self, project):
        _APIVeryGenericProject_Base.__init__(self, project)
        self.__project = project
    
    def SetUseFilePath(self, path):
        self.__project.SetUseFilePath(path)

    def SetConfigFilePath(self, path):
        self.__project.SetConfigFilePath(path)
    

class _APIThirdPartyProject_2_4_5(_APIThirdPartyProject_Base):
    
    def __init__(self, project):
        _APIThirdPartyProject_Base.__init__(self, project)
        self.__project = project


##################
#    Compiler    #
##################

class _APICompiler_Base:
    
    def __init__(self, compiler):
        self.__compiler = compiler
    
    def GetName(self):
        return self.__compiler.GetName()
    
    def TargetIsWindows(self):
        return self.__compiler.IsForPlatform(_WIN32 = True, _NOT_WIN32 = False)
    
    def TargetIsUnix(self):
        return self.__compiler.IsForPlatform(_WIN32 = False, _NOT_WIN32 = True)
    
    def TargetIsLinux(self):
        return self.__compiler.TargetIsLinux()
    
    def TargetIsMac(self):
        return self.__compiler.TargetIsMac()
    
    def TargetIs32Bits(self):
        return self.__compiler.TargetIs32Bits()
    
    def TargetIs64Bits(self):
        return self.__compiler.TargetIs64Bits()
    

class _APICompiler_2_4_5(_APICompiler_Base):
    
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
        return self.__version.GetString(numDecimals) 
    
    def __cmp__(self, other):
        return self.__version.__cmp__(other.__version)


class _APIVersion_2_4_5(_APIVersion_Base):
    
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
    
    def CreateCompiledProject(self, name, type, sourceRootFolder = None, categories = None):
        if sourceRootFolder is None:
            filename = csnProject.FindFilename()
            dirname = os.path.dirname(filename)
            sourceRootFolder = csnUtility.NormalizePath(dirname, _correctCase = False)
        project = GenericProject(name, type, sourceRootFolder, categories, _context=csnProject.globalCurrentContext)
        return self.__genericProjectConstructor(project)

    def CreateStandardModuleProject(self, name, type, sourceRootFolder = None):
        if sourceRootFolder is None:
            filename = csnProject.FindFilename()
            dirname = os.path.dirname(filename)
            sourceRootFolder = csnUtility.NormalizePath(dirname, _correctCase = False)
        project = StandardModuleProject(name, type, sourceRootFolder)
        return self.__standardModuleProjectConstructor(project)

    def CreateThirdPartyProject(self, name, sourceRootFolder = None):
        if sourceRootFolder is None:
            filename = csnProject.FindFilename()
            dirname = os.path.dirname(filename)
            sourceRootFolder = csnUtility.NormalizePath(dirname, _correctCase = False)
        project = ThirdPartyProject(name, csnProject.globalCurrentContext, sourceRootFolder)
        return self.__thirdPartyProjectConstructor(project)
    
    def RewrapProject(self, project):
        project = _UnwrapProject(project)
        if isinstance(project, GenericProject):
            return self.__genericProjectConstructor(project)
        elif isinstance(project, StandardModuleProject):
            return self.__standardModuleProjectConstructor(project)
        elif isinstance(project, ThirdPartyProject):
            return self.__thirdPartyProjectConstructor(project)
        else:
            raise APIError("Unknown project type")
    
    def CreateVersion(self, version):
        return self.__versionConstructor(Version(version))
    
    def GetCSnakeVersion(self):
        return copy.copy(_currentCSnakeVersion)
    
    def GetChosenAPIVersion(self):
        return copy.copy(self.__version)
    
    def LoadThirdPartyModule(self, subFolder, name):
        return csnProject.LoadThirdPartyModule(subFolder, name)
    
    def LoadModule(self):
        # TODO
        pass
    
    def GetCompiler(self):
        if not self.__compiler:
            self.__compiler = self.__compilerConstructor(csnProject.globalCurrentContext.GetCompiler())
        return self.__compiler
    

class _API_2_4_5(_API_Base):
    
    def __init__(self, version):
        _API_Base.__init__(self, version)


######################
# Constructor Caches #
######################
# In order to not have to search and/or instantiate the same class over and over again, we maintain caches


# API objects

_apiRegister = dict()

class APIError(object):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def FindAPI(version):
    version = Version(version)
    if not version in _apiRegister:
        if version > _currentCSnakeVersion:
            raise APIError("Your CSnake version is too old to compile this code!")
        elif version >= Version([2, 4, 5]):
            _apiRegister[version] = _API_2_4_5(version)
        else:
            # there was no API before this
            raise APIError("Unknown API version")
    return _apiRegister[version]


# GenericProject wrapper constructors

_apiGenericProjectConstructorRegister = dict()

def _FindAPIGenericProjectConstructor(version):
    if not version in _apiGenericProjectConstructorRegister:
        if version > _currentCSnakeVersion:
            raise APIError("Your CSnake version is too old to compile this code!")
        elif version >= Version([2, 4, 5]):
            _apiGenericProjectConstructorRegister[version] = _APIGenericProject_2_4_5
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
        elif version >= Version([2, 4, 5]):
            _apiStandardModuleProjectConstructorRegister[version] = _APIStandardModuleProject_2_4_5
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
        elif version >= Version([2, 4, 5]):
            _apiThirdPartyProjectConstructorRegister[version] = _APIThirdPartyProject_2_4_5
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
        elif version >= Version([2, 4, 5]):
            _apiVersionConstructorRegister[version] = _APIVersion_2_4_5
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
        elif version >= Version([2, 4, 5]):
            _apiCompilerConstructorRegister[version] = _APICompiler_2_4_5
        else:
            # there was no API before this
            raise APIError("Unknown API version")
    return _apiCompilerConstructorRegister[version]

