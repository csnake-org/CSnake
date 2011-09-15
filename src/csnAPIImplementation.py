## @package csnAPIImplementation
# Private implementation of API functions for the communication between csnake files and csnake.
# ATTENTION: DON'T IMPORT THIS DIRECTLY FROM CSNAKE FILES!!!


import csnGenerator

import copy
import re
from csnVersion import Version
from csnProject import GenericProject
import csnProject
from csnStandardModuleProject import StandardModuleProject


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


##################
# GenericProject #
##################

class _APIGenericProject_Base:
    
    def __init__(self, project):
        # Note: As the class _APIStandardModuleProject_2_4_5 uses multiple inheritance and derives in two ways from this
        # class, it is possible that this constructor is called two times. This wouldn't hurt in its current
        # implementation. If you plan to change this constructor, make sure it won't hurt after your change, either.
        self.__project = project
    
    def AddSources(self):
        # TODO
        pass
        
    def SetPrecompiledHeader(self, pch):
        # TODO
        pass
    
    def AddIncludeFolders(self):
        # TODO
        pass
    
    def AddProperties(self):
        # TODO
        pass
    
    def AddLibraries(self):
        # TODO
        pass
    
    def AddFilesToInstall(self):
        # TODO
        pass
    
    def AddLibraryModules(self, modules):
        # TODO
        pass
    
    def AddProjects(self, projects):
        # TODO
        pass
    
    def AddTests(self, param1, param2):
        # TODO
        pass
    
    def AddSourceToTest(self):
        # TODO
        pass
    
    def GenerateWin32Header(self, _generate = True):
        # TODO
        pass
    
    def Glob(self):
        # TODO
        pass
    
    def AddCustomCommand(self):
        # TODO
        pass
    
    def CreateHeader(self, filename = None, variables = None, variablePrefix = None):
        self.__project.CreateHeader(filename, variables, variablePrefix)


class _APIGenericProject_2_4_5(_APIGenericProject_Base):
    
    def __init__(self, version):
        _APIGenericProject_Base.__init__(self, version)


#########################
# StandardModuleProject #
#########################

class _APIStandardModuleProject_Base(_APIGenericProject_Base):
    
    def __init__(self, project):
        self.__project = project
    
    def AddApplications(self, apps):
        # TODO
        pass
    
class _APIStandardModuleProject_2_4_5(_APIStandardModuleProject_Base, _APIGenericProject_2_4_5):
    
    def __init__(self, version):
        _APIGenericProject_Base.__init__(self, version)
        _APIStandardModuleProject_Base.__init__(self, version)


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
        self.__versionConstructor = _FindAPIVersionConstructor(version)
    
    def CreateGenericProject(self, _name, _type, someMoreParameters):
        project = GenericProject(_name, _type, someMoreParameters)
        return self.__genericProjectConstructor(project)

    def CreateStandardModuleProject(self, _name, _type, _sourceRootFolder = None):
        project = StandardModuleProject(_name, _type, _sourceRootFolder = None)
        return self.__standardModuleProjectConstructor(project)
    
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


class _API_2_4_5(_API_Base):
    
    def __init__(self, version):
        _API_Base.__init__(self, version)


######################
# Constructor Caches #
######################
# In order to not have to search and/or instantiate the same class over and over again, we maintain caches


# API objects

_apiRegister = dict()

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

