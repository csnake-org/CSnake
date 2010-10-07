import ConfigParser
import OrderedSet
import re
import csnProject
import csnUtility
import csnKDevelop
import csnVisualStudio2003
import csnVisualStudio2005
import csnVisualStudio2008
from csnListener import ChangeEvent
import os.path

latestFileFormatVersion = 2.1

class ContextData:
    def __init__(self):
        # basic fields
        self.__buildFolder = ""    
        self.__installFolder = ""    
        self.__prebuiltBinariesFolder = ""    
        self.__csnakeFile = ""
        self.__instance = ""
        self.__testRunnerTemplate = "normalRunner.tpl"
        self.__configurationName = ""
        self.__compilername = ""
        self.__cmakePath = ""    
        # used for creating the CMake rule to create tests with CxxTests
        self.__pythonPath = ""
        self.__idePath = ""
        self.__kdevelopProjectFolder = ""
            
        # List of items to filter out of build
        self.__filter = ["Demos", "Applications", "Tests"]

        self.__rootFolders = []
        self.__thirdPartySrcAndBuildFolders = []

        self.__recentlyUsed = list()
        
    def GetBuildFolder(self):
        return self.__buildFolder

    def SetBuildFolder(self, value):
        self.__buildFolder = value

    def GetInstallFolder(self):
        return self.__installFolder

    def SetInstallFolder(self, value):
        self.__installFolder = value

    def GetPrebuiltBinariesFolder(self):
        return self.__prebuiltBinariesFolder

    def GetCsnakeFile(self):
        return self.__csnakeFile

    def SetCsnakeFile(self, value):
        self.__csnakeFile = value

    def GetRootFolders(self):
        return self.__rootFolders

    def _SetRootFolders(self, value):
        ''' Protected, should only be accessed by the Context. '''
        self.__rootFolders = value

    def _GetThirdPartySrcAndBuildFolders(self):
        return self.__thirdPartySrcAndBuildFolders

    def _SetThirdPartySrcAndBuildFolders(self, value):
        ''' Protected, should only be accessed by the Context. '''
        self.__thirdPartySrcAndBuildFolders = value

    def GetInstance(self):
        return self.__instance

    def SetInstance(self, value):
        self.__instance = value

    def GetTestRunnerTemplate(self):
        return self.__testRunnerTemplate

    def GetRecentlyUsed(self):
        return self.__recentlyUsed

    def _SetRecentlyUsed(self, value):
        ''' Protected, should only be accessed by the Context. '''
        self.__recentlyUsed = value

    def GetFilter(self):
        return self.__filter

    def SetFilter(self, value):
        self.__filter = value

    def GetConfigurationName(self):
        return self.__configurationName

    def GetCompilername(self):
        return self.__compilername

    def _SetCompilername(self, value):
        ''' Protected, should only be accessed by the Context. '''
        self.__compilername = value

    def GetCmakePath(self):
        return self.__cmakePath

    def SetCmakePath(self, value):
        self.__cmakePath = value

    def GetPythonPath(self):
        return self.__pythonPath

    def SetPythonPath(self, value):
        self.__pythonPath = value

    def GetIdePath(self):
        return self.__idePath

    def SetIdePath(self, value):
        self.__idePath = value

    def GetKdevelopProjectFolder(self):
        return self.__kdevelopProjectFolder

    def SetKdevelopProjectFolder(self, value):
        self.__kdevelopProjectFolder = value
   
    def Equal(self, other):
        """ Compare two contexts. """
        if self.__buildFolder == other.GetBuildFolder() and \
            self.__installFolder == other.GetInstallFolder() and \
            self.__prebuiltBinariesFolder == other.GetPrebuiltBinariesFolder() and \
            self.__csnakeFile == other.GetCsnakeFile() and \
            self.__rootFolders == other.GetRootFolders() and \
            self.__thirdPartySrcAndBuildFolders == other._GetThirdPartySrcAndBuildFolders() and \
            self.__instance == other.GetInstance() and \
            self.__testRunnerTemplate == other.GetTestRunnerTemplate() and \
            self.__filter == other.GetFilter() and \
            self.__configurationName == other.GetConfigurationName() and \
            self.__compilername == other.GetCompilername() and \
            self.__cmakePath == other.GetCmakePath() and \
            self.__pythonPath == other.GetPythonPath() and \
            self.__idePath == other.GetIdePath() and \
            self.__kdevelopProjectFolder == other.GetKdevelopProjectFolder():
            return True
        # default
        return False
    
class Context(object):
    """
    Contains configuration settings such as source folder/build folder/etc.
    __kdevelopProjectFolder - If generating a KDevelop project, then the KDevelop project file will be
    copied from the build folder to this folder. This is work around for a problem in 
    KDevelop: it does not show the source tree if the kdevelop project file is in the build folder.
    __configurationName -- If "DebugAndRelease", then a Debug and a Release configuration are generated (works with Visual Studio),
    if "Debug" or "Release", then only a single configuration is generated (works with KDevelop and Unix Makefiles).
    """
    def __init__(self):
        # context data
        self.__data = ContextData()  
         
        self.__basicFields = [
            "buildFolder", "installFolder", "prebuiltBinariesFolder", "csnakeFile",
            "instance", "testRunnerTemplate", "configurationName", "compilername",
            "cmakePath", "pythonPath", "idePath", "kdevelopProjectFolder"
        ]
        
        self.__compiler = None

        self.__compilermap = {}
        self.RegisterCompiler(csnKDevelop.KDevelop())
        self.RegisterCompiler(csnKDevelop.Makefile())
        self.RegisterCompiler(csnKDevelop.Eclipse())
        self.RegisterCompiler(csnVisualStudio2003.Compiler())
        self.RegisterCompiler(csnVisualStudio2005.Compiler32())
        self.RegisterCompiler(csnVisualStudio2005.Compiler64())
        self.RegisterCompiler(csnVisualStudio2008.Compiler32())
        self.RegisterCompiler(csnVisualStudio2008.Compiler64())
        
        self.__subCategoriesOf = dict()

        # listeners
        self.__listeners = []
        
    # Getter and Setters ================
    
    def GetData(self):
        return self.__data

    def GetCompiler(self):
        return self.__compiler

    # Getter and Setters on __data ================
    
    def GetBuildFolder(self):
        return self.__data.GetBuildFolder()

    def SetBuildFolder(self, value):
        self.__data.SetBuildFolder(value)
        self.__NotifyListeners(ChangeEvent(self))

    def GetInstallFolder(self):
        return self.__data.GetInstallFolder()

    def SetInstallFolder(self, value):
        self.__data.SetInstallFolde(value)
        self.__NotifyListeners(ChangeEvent(self))

    def GetPrebuiltBinariesFolder(self):
        return self.__data.GetPrebuiltBinariesFolder()

    def GetCsnakeFile(self):
        return self.__data.GetCsnakeFile()

    def SetCsnakeFile(self, value):
        self.__data.SetCsnakeFile(value)
        self.__NotifyListeners(ChangeEvent(self))

    def GetRootFolders(self):
        return self.__data.GetRootFolders()

    def _GetThirdPartySrcAndBuildFolders(self):
        return self.__data._GetThirdPartySrcAndBuildFolders()

    def GetInstance(self):
        return self.__data.GetInstance()

    def SetInstance(self, value):
        self.__data.SetInstance(value)
        self.__NotifyListeners(ChangeEvent(self))

    def GetTestRunnerTemplate(self):
        return self.__data.GetTestRunnerTemplate()

    def GetRecentlyUsed(self):
        return self.__data.GetRecentlyUsed()

    def GetFilter(self):
        return self.__data.GetFilter()

    def SetFilter(self, value):
        value.sort()
        self.__data.SetFilter(value)
        self.__NotifyListeners(ChangeEvent(self))

    def GetConfigurationName(self):
        return self.__data.GetConfigurationName()

    def GetCompilername(self):
        return self.__data.GetCompilername()

    def GetCmakePath(self):
        return self.__data.GetCmakePath()

    def SetCmakePath(self, value):
        self.__data.SetCmakePath(value)
        self.__NotifyListeners(ChangeEvent(self))

    def GetSubCategoriesOf(self):
        return self.__subCategoriesOf

    def GetPythonPath(self):
        return self.__data.GetPythonPath()

    def SetPythonPath(self, value):
        self.__data.SetPythonPath(value)
        self.__NotifyListeners(ChangeEvent(self))

    def GetIdePath(self):
        return self.__data.GetIdePath()

    def SetIdePath(self, value):
        self.__data.SetIdePath(value)
        self.__NotifyListeners(ChangeEvent(self))

    def GetKdevelopProjectFolder(self):
        return self.__data.GetKdevelopProjectFolder()

    def SetKdevelopProjectFolder(self, value):
        self.__data.SetKdevelopProjectFolder(value)
        self.__NotifyListeners(ChangeEvent(self))

    # Methods ================

    def RegisterCompiler(self, compiler):
        self.__compilermap[compiler.GetName()] = compiler
    
    def LoadCompilerName(self, parser):
        activateOutput = False
        # temporary workaround to support old versions of the context file
        compilerfieldnames = ["compilername", "compiler"]
        for compilerfieldname in compilerfieldnames:
            try:
                if activateOutput:
                    print "Try with \"%s\"" % compilerfieldname
                self.__data._SetCompilername(parser.get("CSnake", compilerfieldname))
                if activateOutput:
                    print "Worked"
                return
            except:
                activateOutput = True
                print "Reading field \"%s\" failed!" % compilerfieldname
        if activateOutput:
            print "Stop trying and keep default value"
    
    def Load(self, filename):
        try:
            parser = ConfigParser.ConfigParser()
            parser.read([filename])
            # TODO check version number
            self.__LoadBasicFields(parser)
            self.__LoadRootFolders(parser)
            self.__LoadThirdPartySrcAndBuildFolders(parser)
            self.__LoadRecentlyUsedCSnakeFiles(parser)
            
            # Temporary workaround to support old versions of the context file;
            # later this line as well as the function "LoadCompilerName" can be removed
            self.LoadCompilerName(parser)
            
            self.FindCompiler()
            
            return 1
        except:
            return 0
        
    def __LoadBasicFields(self, parser):
        section = "CSnake"
        self.SetFilter(re.split(";", parser.get(section, "filter")))
        for basicField in self.__basicFields:
            # special name for private variables
            field = "_ContextData__" + basicField
            if parser.has_option(section, basicField) and hasattr(self.__data, field):
                setattr(self.__data, field, parser.get(section, basicField))
            else:
                print "missing basicField: '%s'" % basicField

    def __LoadRootFolders(self, parser):
        section = "RootFolders"
        count = 0
        self.__data._SetRootFolders([])
        while parser.has_option(section, "RootFolder%s" % count):
            self.GetRootFolders().append( parser.get(section, "RootFolder%s" % count) )
            count += 1
        
    def __LoadThirdPartySrcAndBuildFolders(self, parser):
        sectionSrc = "ThirdPartyFolders"
        sectionBuild = "ThirdPartyBuildFolders"
        count = 0
        self.__data._SetThirdPartySrcAndBuildFolders([])
        # new style: multiple folders
        while parser.has_option(sectionSrc, "ThirdPartyFolder%s" % count) and parser.has_option(sectionBuild, "ThirdPartyBuildFolder%s" % count):
            self.AddThirdPartySrcAndBuildFolder( \
                parser.get(sectionSrc, "ThirdPartyFolder%s" % count), parser.get(sectionBuild, "ThirdPartyBuildFolder%s" % count))
            count += 1
        # old style: only one folder 
        if count == 0:
            if parser.has_option("CSnake", "thirdpartyrootfolder") and parser.has_option("CSnake", "thirdpartybuildfolder"):
                self.AddThirdPartySrcAndBuildFolder( \
                    parser.get("CSnake", "thirdpartyrootfolder"), parser.get("CSnake", "thirdpartybuildfolder"))

    def __LoadRecentlyUsedCSnakeFiles(self, parser):
        self.__data._SetRecentlyUsed([])
        count = 0
        section = "RecentlyUsedCSnakeFiles"
        while parser.has_option(section, "instance%s" % count):
            self.AddRecentlyUsed(
                parser.get(section, "instance%s" % count),
                parser.get(section, "csnakeFile%s" % count)
            )
            count += 1
    
    def __SaveRecentlyUsedCSnakeFiles(self, parser):
        section = "RecentlyUsedCSnakeFiles"
        if not parser.has_section(section):
            parser.add_section(section)
        for index in range(len(self.GetRecentlyUsed())):
            parser.set(section, "instance%s" % index, self.GetRecentlyUsed()[index].GetInstance()) 
            parser.set(section, "csnakeFile%s" % index, self.GetRecentlyUsed()[index].GetCsnakeFile()) 

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
        parser = ConfigParser.ConfigParser()
        section = "CSnake"
        parser.add_section(section)
        parser.set(section, "version", str(latestFileFormatVersion))
        rootFolderSection = "RootFolders"
        parser.add_section(rootFolderSection)
        thirdPartyFolderSection = "ThirdPartyFolders"
        parser.add_section(thirdPartyFolderSection)
        thirdPartyBuildFolderSection = "ThirdPartyBuildFolders"
        parser.add_section(thirdPartyBuildFolderSection)

        for basicField in self.__basicFields:
            # special name for private variables
            field = "_ContextData__" + basicField
            parser.set(section, basicField, getattr(self.__data, field))
        
        parser.set(section, "filter", ";".join(self.GetFilter()))
        
        count = 0
        while count < len(self.GetRootFolders()):
            parser.set(rootFolderSection, "RootFolder%s" % count, self.GetRootFolders()[count] )
            count += 1

        count = 0
        while count < len(self._GetThirdPartySrcAndBuildFolders()):
            parser.set(thirdPartyFolderSection, "ThirdPartyFolder%s" % count, self._GetThirdPartySrcAndBuildFolders()[count][0] )
            parser.set(thirdPartyBuildFolderSection, "ThirdPartyBuildFolder%s" % count, self._GetThirdPartySrcAndBuildFolders()[count][1] )
            count += 1

        self.__SaveRecentlyUsedCSnakeFiles(parser)
        
        f = open(filename, 'w')
        parser.write(f)
        f.close()
        
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
        self.__data._GetThirdPartySrcAndBuildFolders().append([srcFolder, buildFolder])
        self.__NotifyListeners(ChangeEvent(self))
        
    def RemoveThirdPartySrcAndBuildFolderByIndex(self, index):
        folders = self.__data._GetThirdPartySrcAndBuildFolders()
        self.__data._SetThirdPartySrcAndBuildFolders(folders[0:index] + folders[index+1:])
        self.__NotifyListeners(ChangeEvent(self))
        
    def MoveUpThirdPartySrcAndBuildFolder(self, index):
        folders = self.__data._GetThirdPartySrcAndBuildFolders()
        self.__data._SetThirdPartySrcAndBuildFolders(folders[0:index-1] + [folders[index], folders[index-1]] + folders[index+1:])
        self.__NotifyListeners(ChangeEvent(self))
        
    def MoveDownThirdPartySrcAndBuildFolder(self, index):
        folders = self.__data._GetThirdPartySrcAndBuildFolders()
        self.__data._SetThirdPartySrcAndBuildFolders(folders[0:index] + [folders[index+1], folders[index]] + folders[index+2:])
        self.__NotifyListeners(ChangeEvent(self))
        
    # ----------------------------
    # Root folders handling 
    # ----------------------------
    
    def GetNumberOfRootFolders(self):
        return len(self.__data.GetRootFolders())

    def GetRootFolder(self, index):
        return self.__data.GetRootFolders()[index]

    def AddRootFolder(self, newRootFolder ):
        
        # Check that the new folder doesn't have the same structure than the old ones
        newRootFolderSubdirs = []
        excludedFolders = ["CVS", ".svn"]
        csnUtility.GetDirs( newRootFolder, newRootFolderSubdirs, excludedFolders )
        for oldRootFolder in self.__data.GetRootFolders():
            oldRootFolderSubdirs = []
            csnUtility.GetDirs( oldRootFolder, oldRootFolderSubdirs, excludedFolders )
            for oldSubDir in oldRootFolderSubdirs:
                for newSubDir in newRootFolderSubdirs:
                    if newSubDir == oldSubDir:
                        message = "Error: The new folder (%s) cannot contain similar subfolders than an already set folder (%s)" % (newRootFolder,oldRootFolder)
                        raise Exception( message )
        
        self.__data.GetRootFolders().append(newRootFolder)
        
        self.__NotifyListeners(ChangeEvent(self))

    def RemoveRootFolder(self, folder):
        self.__data.GetRootFolders().remove(folder)
        self.__NotifyListeners(ChangeEvent(self))
        
    def ExtendRootFolders(self, folders):
        self.__data.GetRootFolders().extend(folders)
        self.__NotifyListeners(ChangeEvent(self))

    # ----------------------------
    # Filter handling 
    # ----------------------------
    
    def HasFilter(self, filter):
        return self.__data.GetFilter().count(filter) != 0
    
    def ResetFilter(self):
        self.__data.SetFilter([])
        self.__NotifyListeners(ChangeEvent(self))
    
    def AddFilter(self, filter):
        self.__data.GetFilter().append(filter)
        self.__data.GetFilter().sort()
        self.__NotifyListeners(ChangeEvent(self))
        
    def RemoveFilter(self, filter):
        self.__data.GetFilter().remove(filter)
        self.__data.GetFilter().sort()
        self.__NotifyListeners(ChangeEvent(self))
    
    # ----------------------------
    # Other
    # ----------------------------
    def FindCompiler(self):
        if self.GetCompilername() != None and self.GetCompilername() != "":
            if self.GetCompiler() is None or self.GetCompiler().GetName() != self.GetCompilername():
                self.__compiler = self.__compilermap[self.GetCompilername()]
                self.__compiler.SetConfigurationName(self.GetConfigurationName())
                self.__data._SetCompilername(self.GetCompiler().GetName())
    
    def CreateProject(self, _name, _type, _sourceRootFolder = None, _categories = None):
        project = csnProject.GenericProject(_name, _type, _sourceRootFolder, _categories, _context = self)
        for flag in self.GetCompiler().GetCompileFlags():
            project.compileManager.private.definitions.append(flag)
        return project
    
    def GetOutputFolder(self, mode):
        # "os.path.join" would be better, but doesn't work in Windows because backslashes are not (yet) escaped by csnake
        return self.GetBuildFolder() + "/" + self.GetCompiler().GetOutputSubFolder(mode)
    
    #thirdPartyBinFolder = property(GetThirdPartyBuildFolder) # for backward compatibility
    
    def HasField(self, field):
        return hasattr(self.__data, field)

    def GetField(self, field):
        return getattr(self.__data, field)
    
    def SetField(self, field, value):
        # Check it the field exists
        if not hasattr(self.__data, field):
            print "SetField with wrong field."
            return False
        # Set the field value if different from the current one
        if getattr(self.__data, field) != value:
            setattr(self.__data, field, value)
            if field == "_ContextData__configurationName" and self.__compiler != None:
                self.__compiler.SetConfigurationName(self.GetConfigurationName())
            self.__NotifyListeners(ChangeEvent(self))
    
    def __NotifyListeners(self, event):
        """ Notify the attached listeners about the event. """
        for listener in self.__listeners:
            listener.Update(event)
        
    def AddListener(self, listener):
        """ Attach a listener to this class. """
        if not listener in self.__listeners:
            self.__listeners.append(listener)

def Load(filename):
    """ Shortcut method to avoid creation and calling Load. """
    context = None
    # Check if the file name is specified
    if filename != None and filename != "":
        # Check if the file exists
        if os.path.exists(filename):
            context = Context()
            okay = context.Load(filename)
    assert okay, "Error loading from %s\n" % filename
    return context
