## @package csnAPIImplementation
# Private implementation of API functions for the communication between csnake files and csnake.
# ATTENTION: DON'T IMPORT THIS DIRECTLY FROM CSNAKE FILES!!!


import csnContext
import csnGenerator
import csnProject

import copy
import re


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


#############
#  Project  #
#############

class _APIProject_Base:
    
    def __init__(self, project):
        self.__project = project
    
    def AddSources(self):
        # TODO
        pass
        
    def SetPrecompiledHeader(self):
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
    
    def AddLibraryModules(self):
        # TODO
        pass
    
    def AddProjects(self):
        # TODO
        pass
    
    def AddTests(self):
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


class _APIProject_2_4_5(_APIProject_Base):
    
    def __init__(self, versionArray):
        _APIProject_Base.__init__(self, versionArray)

#############
#    API    #
#############

class _API_Base:
    
    def __init__(self, versionArray):
        self.__version = versionArray
        self.__projectConstructor = _FindAPIProjectConstructor(versionArray)
    
    def CreateProject(self, _name, _type, someMoreParameters):
        project = None
        # TODO: create project
        self.__projectConstructor(project)
        return 
    
    def GetCSnakeVersion(self):
        return copy.copy(_currentCSnakeVersion)
    
    def GetChosenAPIVersion(self):
        return copy.copy(__version)
    
    def LoadThirdPartyModule(self):
        # TODO
        pass
    
    def LoadModule(self):
        # TODO
        pass


class _API_2_4_5(_API_Base):
    
    def __init__(self, versionArray):
        _API_Base.__init__(self, versionArray)


#############
# Versions  #
#############

_currentCSnakeVersion = map(int, re.match('([0-9\\.]+)(.*)', csnGenerator.version).group(1).split("."))


# Maintain a cache of APIs, so there's no need to instantiate the class over and over again
_apiRegister = dict()

def FindAPI(versionArray):
    if not versionArray in _apiRegister:
        if versionArray > _currentCSnakeVersion:
            raise APIError("Your CSnake version is too old to compile this code!")
        elif versionArray >= [2, 4, 5]:
            _apiRegister[versionArray] = _API_2_4_5(versionArray)
        else:
            # there was no API before this
            raise APIError("Unknown API version")
    return _apiRegister[versionArray]


# Maintain a cache of constructors
_apiProjectConstructorRegister = dict()

def _FindAPIProjectConstructor(versionArray):
    if not versionArray in _apiProjectConstructorRegister:
        if versionArray > _currentCSnakeVersion:
            raise APIError("Your CSnake version is too old to compile this code!")
        elif versionArray >= [2, 4, 5]:
            _apiProjectConstructorRegister[versionArray] = _APIProject_2_4_5
        else:
            # there was no API before this
            raise APIError("Unknown API version")
    return _apiProjectConstructorRegister[versionArray]

