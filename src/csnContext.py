## @package csnContext
# Definition of the Context and ContextData class. 
import ConfigParser
import OrderedSet
import re
import csnProject
import csnUtility
import csnKDevelop
import csnVisualStudio2003
import csnVisualStudio2005
import csnVisualStudio2008
import csnVisualStudio2010
from csnListener import ChangeEvent
import os.path
import shutil

latestFileFormatVersion = 2.2

def WriteHeaderComments(f):
    """ Helper function that writes some comments into file f """
    f.write(";CSnake context file.\n")
    f.write(";Before manually editing this file, close any instance of\n")
    f.write(";CSnakeGUI using this context, or changes will be lost.\n")
    f.write("\n")

class Context(object):
    """
    Contains configuration settings such as source folder/build folder/etc.
    kdevelopProjectFolder - If generating a KDevelop project, then the KDevelop project file will be
    copied from the build folder to this folder. This is work around for a problem in
    KDevelop: it does not show the source tree if the kdevelop project file is in the build folder.
    configurationName -- If "DebugAndRelease", then a Debug and a Release configuration are generated (works with Visual Studio),
    if "Debug" or "Release", then only a single configuration is generated (works with KDevelop and Unix Makefiles).
    """
    def __init__(self):
        # basic fields
        self.buildFolder = ""
        self.installFolder = ""
        self.prebuiltBinariesFolder = ""
        self.csnakeFile = ""
        self.instance = ""
        self.testRunnerTemplate = "normalRunner.tpl"
        self.configurationName = ""
        self.compilername = "Visual Studio 7 .NET 2003"
        self.cmakePath = ""
        # used for creating the CMake rule to create tests with CxxTests
        self.pythonPath = ""
        self.cmakeVersion = "2.8"
        self.idePath = ""
        self.kdevelopProjectFolder = ""

        # List of items to filter out of build
        self.filter = ["Demos", "Applications", "Tests", "Plugins"]

        self.rootFolders = []
        self.thirdPartySrcAndBuildFolders = []

        self.recentlyUsed = list()

        # basic fields: the key is the class member, the value its option in the parser
        self.basicFields = {
            "buildFolder": "buildFolder",
            "installFolder": "installFolder",
            "prebuiltBinariesFolder": "prebuiltBinariesFolder",
            "csnakeFile": "csnakeFile",
            "instance": "instance",
            "testRunnerTemplate": "testRunnerTemplate",
            "configurationName": "configurationName",
            "compilername": "compilername",
            "cmakePath": "cmakePath",
            "cmakeVersion" : "cmakeVersion",
            "pythonPath": "pythonPath",
            "idePath": "idePath",
            "kdevelopProjectFolder": "kdevelopProjectFolder"
        }

        self.compiler = None

        self.compilermap = {}
        self.RegisterCompiler(csnKDevelop.KDevelop())
        self.RegisterCompiler(csnKDevelop.Makefile())
        self.RegisterCompiler(csnKDevelop.Eclipse())
        self.RegisterCompiler(csnVisualStudio2003.Compiler())
        self.RegisterCompiler(csnVisualStudio2005.Compiler32())
        self.RegisterCompiler(csnVisualStudio2005.Compiler64())
        self.RegisterCompiler(csnVisualStudio2008.Compiler32())
        self.RegisterCompiler(csnVisualStudio2008.Compiler64())
        self.RegisterCompiler(csnVisualStudio2010.Compiler32())
        self.RegisterCompiler(csnVisualStudio2010.Compiler64())

        self.subCategoriesOf = dict()

        # listeners
        self.listeners = []

    # Getter and Setters ================

    def GetCompiler(self):
        return self.compiler

    # Getter and Setters on data ================

    def GetBuildFolder(self):
        return self.buildFolder

    def SetBuildFolder(self, value):
        self.buildFolder = value
        self.__NotifyListeners(ChangeEvent(self))

    def GetInstallFolder(self):
        return self.installFolder

    def SetInstallFolder(self, value):
        self.installFolder = value
        self.__NotifyListeners(ChangeEvent(self))

    def GetPrebuiltBinariesFolder(self):
        return self.prebuiltBinariesFolder

    def GetCsnakeFile(self):
        return self.csnakeFile

    def SetCsnakeFile(self, value):
        self.csnakeFile = value
        self.__NotifyListeners(ChangeEvent(self))

    def GetRootFolders(self):
        return self.rootFolders

    def SetRootFolders(self, value):
        self.rootFolders = value

    def _GetThirdPartySrcAndBuildFolders(self):
        return self.thirdPartySrcAndBuildFolders

    def GetInstance(self):
        return self.instance

    def SetInstance(self, value):
        self.instance = value
        # reset the filter
        self.SetFilter([])
        self.__NotifyListeners(ChangeEvent(self))

    def GetTestRunnerTemplate(self):
        return self.testRunnerTemplate

    def GetRecentlyUsed(self):
        return self.recentlyUsed

    def SetRecentlyUsed(self, value):
        recentlyUsed = value

    def GetFilter(self):
        return self.filter

    def SetFilter(self, value):
        value.sort()
        self.filter = value
        self.__NotifyListeners(ChangeEvent(self))

    def GetConfigurationName(self):
        return self.configurationName

    def GetCompilername(self):
        return self.compilername

    def SetCompilername(self, value):
        self.compilername = value

    def GetCmakePath(self):
        return self.cmakePath

    def SetCmakePath(self, value):
        self.cmakePath = value
        self.__NotifyListeners(ChangeEvent(self))

    def GetSubCategoriesOf(self):
        return self.subCategoriesOf

    def GetPythonPath(self):
        return self.pythonPath

    def SetPythonPath(self, value):
        self.pythonPath = value
        self.__NotifyListeners(ChangeEvent(self))

    def GetIdePath(self):
        return self.idePath

    def SetIdePath(self, value):
        self.idePath = value
        self.__NotifyListeners(ChangeEvent(self))

    def GetKdevelopProjectFolder(self):
        return self.kdevelopProjectFolder

    def SetKdevelopProjectFolder(self, value):
        self.kdevelopProjectFolder = value
        self.__NotifyListeners(ChangeEvent(self))

    def GetThirdPartySrcAndBuildFolders(self):
        return self.thirdPartySrcAndBuildFolders

    def SetThirdPartySrcAndBuildFolders(self, value):
        ''' Protected, should only be accessed by the Context. '''
        self.thirdPartySrcAndBuildFolders = value

    # Methods ================

    def RegisterCompiler(self, compiler):
        self.compilermap[compiler.GetName()] = compiler

    def Load(self, filename):
        """ Load a context file. """
        # parser
        parser = ConfigParser.ConfigParser()
        parser.read([filename])
        # check main section
        mainSection = "CSnake"
        if not parser.has_section(mainSection):
            raise IOError("Cannot read context, no 'CSnake' section.")
        # check version number
        version = 0.0
        if parser.has_option(mainSection, "version"):
            version = float(parser.get(mainSection, "version"))
        # read with proper reader
        if version == 0.0:
            self.__Read00( parser )
        elif version == 1.0:
            self.__Read10( parser )
        elif version == 2.0:
            self.__Read20( parser )
        elif version == 2.1:
            self.__Read21( parser )
        elif version == 2.2:
            self.__Read22( parser )
        else:
            raise IOError("Cannot read context, unknown 'version':%s." % version)
        # backup and save in new format for old ones
        if version < latestFileFormatVersion:
            newFileName = "%s.bk" % filename
            shutil.copy(filename, newFileName)
            self.Save(filename)

    def __Read00(self, parser):
        """ Read options file version 1.0. """
        # basic fields
        basicFields = {
            "buildFolder": "binfolder",
            "installFolder": "installFolder",
            "prebuiltBinariesFolder": "prebuiltBinariesFolder",
            "csnakeFile": "csnakeFile",
            "instance": "instance",
            "testRunnerTemplate": "testRunnerTemplate",
        }
        self.__LoadBasicFields(parser, basicFields)
        # this version stores fields in the options file
        optionsFilename = "options"
        if os.path.isfile(optionsFilename):
            basicOptionsFields = {
                "configurationName": "cmakebuildtype",
                "compilername": "compiler",
                "cmakePath": "cmakepath",
                "pythonPath": "pythonpath",
                "idePath": "visualstudiopath"
            }
            optionsParser = ConfigParser.ConfigParser()
            optionsParser.read([optionsFilename])
            self.__LoadBasicFields(optionsParser, basicOptionsFields)
        else:
            raise IOError("Could not retrieve the option file.")
        self.SetFilter(re.split(";", parser.get("CSnake", "filter")))
        # root folders
        self.__LoadRootFolders(parser)
        # third parties
        self.__LoadThirdPartySrcAndBinFolders(parser)
        # recent files
        self.__LoadRecentlyUsedCSnakeFilesMulitpleSection(parser)
        # find the compiler from the compiler name
        self.FindCompiler()

    def __Read10(self, parser):
        """ Read options file version 1.0. """
        # basic fields
        basicFields = {
            "buildFolder": "binfolder",
            "installFolder": "installFolder",
            "prebuiltBinariesFolder": "prebuiltBinariesFolder",
            "csnakeFile": "csnakeFile",
            "instance": "instance",
            "testRunnerTemplate": "testRunnerTemplate",
        }
        self.__LoadBasicFields(parser, basicFields)
        # this version stores fields in the options file
        optionsFilename = "options"
        if os.path.isfile(optionsFilename):
            basicOptionsFields = {
                "configurationName": "cmakebuildtype",
                "compilername": "compiler",
                "cmakePath": "cmakepath",
                "pythonPath": "pythonpath",
                "idePath": "visualstudiopath"
            }
            optionsParser = ConfigParser.ConfigParser()
            optionsParser.read([optionsFilename])
            self.__LoadBasicFields(optionsParser, basicOptionsFields)
        else:
            raise IOError("Could not retrieve the option file.")
        self.SetFilter(re.split(";", parser.get("CSnake", "filter")))
        # root folders
        self.__LoadRootFolders(parser)
        # third parties
        self.__LoadThirdPartySrcAndBuildFoldersSingle(parser)
        # recent files
        self.__LoadRecentlyUsedCSnakeFilesMulitpleSection(parser)
        # find the compiler from the compiler name
        self.FindCompiler()

    def __Read20(self, parser):
        """ Read options file version 2.0. """
        # basic fields
        # diff to 2.1: compiler, no kdevelop
        basicFields = {
            "buildFolder": "buildFolder",
            "installFolder": "installFolder",
            "prebuiltBinariesFolder": "prebuiltBinariesFolder",
            "csnakeFile": "csnakeFile",
            "instance": "instance",
            "testRunnerTemplate": "testRunnerTemplate",
            "configurationName": "configurationName",
            "cmakePath": "cmakePath",
            "pythonPath": "pythonPath",
            "idePath": "idePath"
        }
        self.__LoadBasicFields(parser, basicFields)
        self.__LoadCompiler(parser)
        self.SetFilter(re.split(";", parser.get("CSnake", "filter")))
        # root folders
        self.__LoadRootFolders(parser)
        # third parties: mix between multiple and single folders...
        if parser.has_section("ThirdPartyFolders") and parser.has_section("ThirdPartyBuildFolders"):
            self.__LoadThirdPartySrcAndBuildFoldersMultiple(parser)
        elif parser.has_option("CSnake", "thirdpartyrootfolder") and parser.has_option("CSnake", "thirdpartybuildfolder"):
            self.__LoadThirdPartySrcAndBuildFoldersSingle(parser)
        else:
            raise IOError("Missing third parties (single or multiple).")
        # recent files
        self.__LoadRecentlyUsedCSnakeFilesOneSection(parser)
        # find the compiler from the compiler name
        self.FindCompiler()

    def __Read21(self, parser):
        """ Read options file version 2.1. """
        # basic fields
        basicFields = {
            "buildFolder": "buildFolder",
            "installFolder": "installFolder",
            "prebuiltBinariesFolder": "prebuiltBinariesFolder",
            "csnakeFile": "csnakeFile",
            "instance": "instance",
            "testRunnerTemplate": "testRunnerTemplate",
            "configurationName": "configurationName",
            "compilername": "compilername",
            "cmakePath": "cmakePath",
            "pythonPath": "pythonPath",
            "idePath": "idePath",
            "kdevelopProjectFolder": "kdevelopProjectFolder"
        }
        self.__LoadBasicFields(parser, basicFields)
        self.SetFilter(re.split(";", parser.get("CSnake", "filter")))
        # root folders
        self.__LoadRootFolders(parser)
        # third parties: now multiple
        self.__LoadThirdPartySrcAndBuildFoldersMultiple(parser)
        # recent files
        self.__LoadRecentlyUsedCSnakeFilesOneSection(parser)
        # find the compiler from the compiler name
        self.FindCompiler()
        
    def __Read22(self, parser):
        """ Read options file version 2.1. """
        # basic fields
        self.__LoadBasicFields(parser, self.basicFields)
        self.SetFilter(re.split(";", parser.get("CSnake", "filter")))
        # root folders
        self.__LoadRootFolders(parser)
        # third parties: now multiple
        self.__LoadThirdPartySrcAndBuildFoldersMultiple(parser)
        # recent files
        self.__LoadRecentlyUsedCSnakeFilesOneSection(parser)
        # find the compiler from the compiler name
        self.FindCompiler()

    def __LoadBasicFields(self, parser, fields):
        """ Load a list of fields. """
        # section
        section = "CSnake"
        # read
        for key in fields.keys():
            # special name for private variables
            attribute = key
            if not hasattr(self, attribute):
                raise IOError("Missing attribute: '%s'" % attribute)
            # field
            field = fields[key]
            if not parser.has_option(section, field):
                raise IOError("Missing field: '%s'" % field)
            # set
            setattr(self, attribute, parser.get(section, field))

    def __LoadCompiler(self, parser):
        """ Load the compiler either from 'compiler' or 'compilername'. """
        # section
        section = "CSnake"
        # read
        field = None
        if parser.has_option(section, "compilername"):
            field = "compilername"
        elif parser.has_option(section, "compiler"):
            field = "compiler"
        # error
        if not field:
            raise IOError("Missing field: compiler or compilername")
        # set    
        self.SetCompilername(parser.get(section, field))
        
    def __LoadRootFolders(self, parser):
        """ Load root folders. Used in from v0.0. """
        # section
        section = "RootFolders"
        # clear array
        self.SetRootFolders([])
        # read
        count = 0
        while parser.has_option(section, "RootFolder%s" % count):
            self.GetRootFolders().append( parser.get(section, "RootFolder%s" % count) )
            count += 1
        
    def __LoadThirdPartySrcAndBuildFoldersMultiple(self, parser):
        """ Load third party src and build folders. Used from v2.1. """
        # sections
        sectionSrc = "ThirdPartyFolders"
        sectionBuild = "ThirdPartyBuildFolders"
        # clear array
        self.SetThirdPartySrcAndBuildFolders([])
        # read 
        count = 0
        # new style: multiple folders
        while parser.has_option(sectionSrc, "ThirdPartyFolder%s" % count) and parser.has_option(sectionBuild, "ThirdPartyBuildFolder%s" % count):
            self.AddThirdPartySrcAndBuildFolder( \
                parser.get(sectionSrc, "ThirdPartyFolder%s" % count), parser.get(sectionBuild, "ThirdPartyBuildFolder%s" % count))
            count += 1

    def __LoadThirdPartySrcAndBuildFoldersSingle(self, parser):
        """ Load third party src and build folders. Used in v1.0. """
        # sections
        section = "CSnake"
        # clear array
        self.SetThirdPartySrcAndBuildFolders([])
        # read 
        self.AddThirdPartySrcAndBuildFolder(
            parser.get(section, "thirdpartyrootfolder"), 
            parser.get(section, "thirdpartybuildfolder") )

    def __LoadThirdPartySrcAndBinFolders(self, parser):
        """ Load third party src and build folders. Used in v0.0. """
        # sections
        section = "CSnake"
        # clear array
        self.SetThirdPartySrcAndBuildFolders([])
        # read 
        self.AddThirdPartySrcAndBuildFolder(
            parser.get(section, "thirdpartyrootfolder"), 
            parser.get(section, "thirdpartybinfolder") )

    def __LoadRecentlyUsedCSnakeFilesMulitpleSection(self, parser):
        """ Load recently used files. Used in v <= 1.0. """
        # section
        sectionRoot = "RecentlyUsedCSnakeFiles"
        # clear array
        self.SetRecentlyUsed([])
        # read
        count = 0
        section = "%s%s" % (sectionRoot, count)
        while parser.has_section(section):
            self.AddRecentlyUsed(
                parser.get(section, "instance%s" % count), 
                parser.get(section, "csnakeFile%s" % count) )
            count += 1
            section = "%s%s" % (sectionRoot, count)


    def __LoadRecentlyUsedCSnakeFilesOneSection(self, parser):
        """ Load recently used files. Used from v2.0. """
        # section
        section = "RecentlyUsedCSnakeFiles"
        # clear array
        self.SetRecentlyUsed([])
        # read
        count = 0
        while parser.has_option(section, "instance%s" % count):
            self.AddRecentlyUsed(
                parser.get(section, "instance%s" % count), 
                parser.get(section, "csnakeFile%s" % count) )
            count += 1
    
    def AddRecentlyUsed(self, instance, csnakeFile):
        for item in range( len(self.GetRecentlyUsed()) ):
            x = self.GetRecentlyUsed()[item]
            if (x.GetInstance() == instance and x.GetCsnakeFile() == csnakeFile):
                self.GetRecentlyUsed().remove(x)
                self.GetRecentlyUsed().insert(0, x)
                return
        
        x = Context()
        x.SetInstance(instance)
        x.SetCsnakeFile(csnakeFile)
        self.GetRecentlyUsed().insert(0, x)
    
    def IsCSnakeFileInRecentlyUsed(self):
        """ Returns True if the csnakeFile is in the list of recently used csnake files """
        result = False
        for item in range( len(self.GetRecentlyUsed()) ):
            x = self.GetRecentlyUsed()[item]
            if (x.GetCsnakeFile() == self.GetCsnakeFile()):
                result = True
        return result
    
    def Save(self, filename):
        """ Save a context file. """
        # file parser
        parser = ConfigParser.ConfigParser()
        
        # main section 
        mainSection = "CSnake"
        parser.add_section(mainSection)
        # set the version
        parser.set(mainSection, "version", latestFileFormatVersion)
        # set the basic fields
        for basicField in self.basicFields:
            # special name for private variables
            field = basicField
            parser.set(mainSection, basicField, getattr(self, field))
        # set the filter
        parser.set(mainSection, "filter", ";".join(self.GetFilter()))
        
        # root folders
        rootFolderSection = "RootFolders"
        parser.add_section(rootFolderSection)
        count = 0
        while count < len(self.GetRootFolders()):
            parser.set(rootFolderSection, "RootFolder%s" % count, self.GetRootFolders()[count] )
            count += 1
        
        # third parties src and build folders    
        thirdPartyFolderSection = "ThirdPartyFolders"
        parser.add_section(thirdPartyFolderSection)
        thirdPartyBuildFolderSection = "ThirdPartyBuildFolders"
        parser.add_section(thirdPartyBuildFolderSection)
        count = 0
        while count < len(self._GetThirdPartySrcAndBuildFolders()):
            parser.set(thirdPartyFolderSection, "ThirdPartyFolder%s" % count, self._GetThirdPartySrcAndBuildFolders()[count][0] )
            parser.set(thirdPartyBuildFolderSection, "ThirdPartyBuildFolder%s" % count, self._GetThirdPartySrcAndBuildFolders()[count][1] )
            count += 1
        
        # recent files
        recentSection = "RecentlyUsedCSnakeFiles"
        parser.add_section(recentSection)
        for index in range(len(self.GetRecentlyUsed())):
            parser.set(recentSection, "instance%s" % index, self.GetRecentlyUsed()[index].GetInstance()) 
            parser.set(recentSection, "csnakeFile%s" % index, self.GetRecentlyUsed()[index].GetCsnakeFile()) 
        
        # write the file
        f = open(filename, 'w')
        parser.write(f)
        f.close()

    def Dump(self):
		return { \
			"buildFolder" : self.GetBuildFolder(), \
            "installFolder" : self.GetInstallFolder(), \
            "prebuiltBinariesFolder" : self.GetPrebuiltBinariesFolder(), \
            "csnakeFile" : self.GetCsnakeFile(), \
            "rootFolders" : self.GetRootFolders(), \
            "thirdPartySrcAndBuildFolders" : self._GetThirdPartySrcAndBuildFolders(), \
            "instance" : self.GetInstance(), \
            "testRunnerTemplate" : self.GetTestRunnerTemplate(), \
            "filter" : self.GetFilter(), \
            "configurationName" : self.GetConfigurationName(), \
            "compilername" : self.GetCompilername(), \
            "cmakeVersion" : self.cmakeVersion, \
            "cmakePath" : self.GetCmakePath(), \
            "pythonPath" : self.GetPythonPath(), \
            "idePath" : self.GetIdePath(), \
            "kdevelopProjectFolder" : self.GetKdevelopProjectFolder()
		}
        
    # ----------------------------
    # Sub categories handling 
    # ----------------------------
    
    def SetSuperSubCategory(self, super, sub):
        """ 
        Makes super a supercategory of sub. This information is used to be able to disable all Tests with a single
        click (since Tests will be a supercategory of each Test project).
        """
        if not self.GetSubCategoriesOf().has_key(super):
            self.GetSubCategoriesOf()[super] = OrderedSet.OrderedSet()
        self.GetSubCategoriesOf()[super].add(sub)
        self.__NotifyListeners(ChangeEvent(self))
        
    # ----------------------------
    # Third party handling 
    # ----------------------------
    
    def GetThirdPartyBuildFolderByIndex(self, index):
        # "os.path.join" would be better, but doesn't work in Windows because backslashes are not (yet) escaped by csnake
        return self._GetThirdPartySrcAndBuildFolders()[index][1] + "/" + self.GetCompiler().GetThirdPartySubFolder()

    def GetThirdPartyBuildFolders(self):
        result = []
        for srcAndBuildFolder in self._GetThirdPartySrcAndBuildFolders():
            result.append(srcAndBuildFolder[1])
        return result
    
    def GetThirdPartyBuildFoldersComplete(self):
        GetThirdPartyBuildFoldersComplete = []
        for srcAndBuildFolder in self._GetThirdPartySrcAndBuildFolders():
            GetThirdPartyBuildFoldersComplete.append(srcAndBuildFolder[1] + "/" + self.GetCompiler().GetThirdPartySubFolder())
        return GetThirdPartyBuildFoldersComplete
    
    def GetThirdPartyFolder(self, index = 0):
        return self._GetThirdPartySrcAndBuildFolders()[index][0]

    def GetThirdPartyFolders(self):
        result = []
        for srcAndBuildFolder in self._GetThirdPartySrcAndBuildFolders():
            result.append(srcAndBuildFolder[0])
        return result

    def GetNumberOfThirdPartyFolders( self ):
        return len(self._GetThirdPartySrcAndBuildFolders())
    
    def AddThirdPartySrcAndBuildFolder(self, srcFolder = "", buildFolder = ""):
        self.GetThirdPartySrcAndBuildFolders().append([srcFolder, buildFolder])
        self.__NotifyListeners(ChangeEvent(self))
        
    def RemoveThirdPartySrcAndBuildFolderByIndex(self, index):
        folders = self.GetThirdPartySrcAndBuildFolders()
        self.SetThirdPartySrcAndBuildFolders(folders[0:index] + folders[index+1:])
        self.__NotifyListeners(ChangeEvent(self))
        
    def MoveUpThirdPartySrcAndBuildFolder(self, index):
        folders = self.GetThirdPartySrcAndBuildFolders()
        self.SetThirdPartySrcAndBuildFolders(folders[0:index-1] + [folders[index], folders[index-1]] + folders[index+1:])
        self.__NotifyListeners(ChangeEvent(self))
        
    def MoveDownThirdPartySrcAndBuildFolder(self, index):
        folders = self.GetThirdPartySrcAndBuildFolders()
        self.SetThirdPartySrcAndBuildFolders(folders[0:index] + [folders[index+1], folders[index]] + folders[index+2:])
        self.__NotifyListeners(ChangeEvent(self))
        
    def __CheckThirdPartyArray(self, array):
        """ Check if the third party array is correct. """
        for firstPair in array:
            arrayCopy = array[:]
            arrayCopy.remove(firstPair)
            for secondPair in arrayCopy:
                if( secondPair[0] == firstPair[0] and secondPair[1] == firstPair[1]):
                    return "Duplicate entry: %s, %s == %s, %s" % (secondPair[0], secondPair[1], firstPair[0], firstPair[1])
                if( secondPair[1] == firstPair[1] ):
                    return "Duplicate build folder: %s" % secondPair[1]
        return True
        
    # ----------------------------
    # Root folders handling 
    # ----------------------------
    
    def GetNumberOfRootFolders(self):
        return len(self.GetRootFolders())

    def GetRootFolder(self, index):
        return self.GetRootFolders()[index]

    def AddRootFolder(self, newRootFolder ):
        
        # Check that the new folder doesn't have the same structure than the old ones
        newRootFolderSubdirs = []
        excludedFolders = ["CVS", ".svn", "data"]
        csnUtility.GetDirs( newRootFolder, newRootFolderSubdirs, excludedFolders )
        for oldRootFolder in self.GetRootFolders():
            oldRootFolderSubdirs = []
            csnUtility.GetDirs( oldRootFolder, oldRootFolderSubdirs, excludedFolders )
            for oldSubDir in oldRootFolderSubdirs:
                for newSubDir in newRootFolderSubdirs:
                    if newSubDir == oldSubDir:
                        message = "Error: The new folder (%s) cannot contain similar subfolders than an already set folder (%s)" % (newRootFolder,oldRootFolder)
                        raise Exception( message )
        
        self.GetRootFolders().append(newRootFolder)
        
        self.__NotifyListeners(ChangeEvent(self))

    def RemoveRootFolder(self, folder):
        self.GetRootFolders().remove(folder)
        self.__NotifyListeners(ChangeEvent(self))
        
    def ExtendRootFolders(self, folders):
        self.GetRootFolders().extend(folders)
        self.__NotifyListeners(ChangeEvent(self))

    # ----------------------------
    # Filter handling 
    # ----------------------------
    
    def HasFilter(self, filter):
        return self.GetFilter().count(filter) != 0
    
    def ResetFilter(self):
        self.SetFilter([])
        self.__NotifyListeners(ChangeEvent(self))
    
    def AddFilter(self, filter):
        self.GetFilter().append(filter)
        self.GetFilter().sort()
        self.__NotifyListeners(ChangeEvent(self))
        
    def RemoveFilter(self, filter):
        self.GetFilter().remove(filter)
        self.GetFilter().sort()
        self.__NotifyListeners(ChangeEvent(self))
    
    # ----------------------------
    # Other
    # ----------------------------
    def FindCompiler(self):
        compilerName = self.GetCompilername()
        if compilerName != None and compilerName != "" and compilerName in self.compilermap:
            if self.GetCompiler() is None or self.GetCompiler().GetName() != self.GetCompilername():
                self.compiler = self.compilermap[self.GetCompilername()]
                self.compiler.SetConfigurationName(self.GetConfigurationName())
                self.SetCompilername(self.GetCompiler().GetName())
        else:
            raise IOError("Unknown compiler: %s" % compilerName)
        
    def CreateProject(self, _name, _type, _sourceRootFolder = None, _categories = None):
        project = csnProject.GenericProject(_name, _type, _sourceRootFolder, _categories, _context = self)
        for flag in self.GetCompiler().GetCompileFlags():
            project.compileManager.private.definitions.append(flag)
        return project
    
    def GetOutputFolder(self, mode):
        # "os.path.join" would be better, but doesn't work in Windows because backslashes are not (yet) escaped by csnake
        return self.buildFolder + "/" + self.GetCompiler().GetOutputSubFolder(mode)
    
    #thirdPartyBinFolder = property(GetThirdPartyBuildFolder) # for backward compatibility
    
    def HasField(self, field):
        return hasattr(self, field)

    def GetField(self, field):
        return getattr(self, field)
    
    def CheckField(self, field, value):
        """ Check the field before setting it. 
        Return True if ok or otherwise an error message. """
        # Check it the field exists
        if not hasattr(self, field):
            raise AttributeError("SetField with wrong field.")
        # Check the field value if different from the current one
        if getattr(self, field) != value:
            # third parties
            if field == "thirdPartySrcAndBuildFolders":
                return self.__CheckThirdPartyArray(value)
        # default
        return True

    def SetField(self, field, value):
        # Set the field value if different from the current one
        if getattr(self, field) != value:
            # set the attribute
            setattr(self, field, value)
            # post-process
            if field == "configurationName" and self.compiler != None:
                self.compiler.SetConfigurationName(self.GetConfigurationName())
            elif field == "instance":
                # reset the filter
                self.SetFilter([])
            # notify
            self.__NotifyListeners(ChangeEvent(self))
    
    def __NotifyListeners(self, event):
        """ Notify the attached listeners about the event. """
        for listener in self.listeners:
            listener.Update(event)
        
    def AddListener(self, listener):
        """ Attach a listener to this class. """
        if not listener in self.listeners:
            self.listeners.append(listener)

def Load(filename):
    """ Shortcut method to avoid creation and calling Load. """
    context = None
    # Check if the file name is specified
    if filename != None and filename != "":
        # Check if the file exists
        if os.path.exists(filename):
            context = Context()
            context.Load(filename)
    return context
