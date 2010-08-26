import ConfigParser
import OrderedSet
import re
import csnProject
import csnUtility

latestFileFormatVersion = 2.0

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
        # basic fields
        self.__buildFolder = ""    
        self.__installFolder = ""    
        self.__prebuiltBinariesFolder = ""    
        self.__csnakeFile = ""
        self.__instance = ""
        self.__testRunnerTemplate = "normalRunner.tpl"
        self.__configurationName = "DebugAndRelease"
        self.__compilername = "Visual Studio 9 2008 Win64"
        self.__cmakePath = ""    
        # used for creating the CMake rule to create tests with CxxTests
        self.__pythonPath = ""
        self.__idePath = ""
        self.__kdevelopProjectFolder = ""
            
        self.__basicFields = [
            "buildFolder", "installFolder", "prebuiltBinariesFolder", "csnakeFile",
            "instance", "testRunnerTemplate", "configurationName", "compilername",
            "cmakePath", "pythonPath", "idePath", "kdevelopProjectFolder"
        ]
        
        self.__compiler = None
        self.__filter = ["Demos", "Applications", "Tests"]

        self.__rootFolders = []
        self.__thirdPartySrcAndBuildFolders = []

        self.__recentlyUsed = list()
        self.__subCategoriesOf = dict()
        
        self.__compilermap = {}
        self.RegisterCompiler(csnKDevelop.KDevelop())
        self.RegisterCompiler(csnKDevelop.Makefile())
        self.RegisterCompiler(csnKDevelop.Eclipse())
        self.RegisterCompiler(csnVisualStudio2003.Compiler())
        self.RegisterCompiler(csnVisualStudio2005.Compiler32())
        self.RegisterCompiler(csnVisualStudio2005.Compiler64())
        self.RegisterCompiler(csnVisualStudio2008.Compiler32())
        self.RegisterCompiler(csnVisualStudio2008.Compiler64())

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

    def GetThirdPartySrcAndBuildFolders(self):
        return self.__thirdPartySrcAndBuildFolders

    def GetInstance(self):
        return self.__instance

    def SetInstance(self, value):
        self.__instance = value

    def GetTestRunnerTemplate(self):
        return self.__testRunnerTemplate

    def GetRecentlyUsed(self):
        return self.__recentlyUsed

    def GetFilter(self):
        return self.__filter

    def SetFilter(self, value):
        self.__filter = value

    def GetConfigurationName(self):
        return self.__configurationName

    def GetCompilername(self):
        return self.__compilername

    def GetCompiler(self):
        return self.__compiler

    def GetCmakePath(self):
        return self.__cmakePath

    def SetCmakePath(self, value):
        self.__cmakePath = value

    def GetSubCategoriesOf(self):
        return self.__subCategoriesOf

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

    def RegisterCompiler(self, compiler):
        self.__compilermap[compiler.GetName()] = compiler
        compiler.context = self
    
    def LoadCompilerName(self, parser):
        activateOutput = False
        # temporary workaround to support old versions of the context file
        compilerfieldnames = ["compilername", "compiler"]
        for compilerfieldname in compilerfieldnames:
            try:
                if activateOutput:
                    print "Try with \"%s\"" % compilerfieldname
                self.__compilername = parser.get("CSnake", compilerfieldname)
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
        self.__filter = re.split(";", parser.get(section, "filter"))
        for basicField in self.__basicFields:
            if parser.has_option(section, basicField):
                # special name for private variables
                field = "_Context__" + basicField
                setattr(self, field, parser.get(section, basicField))

    def __LoadRootFolders(self, parser):
        section = "RootFolders"
        count = 0
        self.__rootFolders = []
        while parser.has_option(section, "RootFolder%s" % count):
            self.__rootFolders.append( parser.get(section, "RootFolder%s" % count) )
            count += 1
        
    def __LoadThirdPartySrcAndBuildFolders(self, parser):
        sectionSrc = "ThirdPartyFolders"
        sectionBuild = "ThirdPartyBuildFolders"
        count = 0
        self.__thirdPartySrcAndBuildFolders = []
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
        self.__recentlyUsed = []
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
        for index in range(len(self.__recentlyUsed)):
            parser.set(section, "instance%s" % index, self.__recentlyUsed[index].__instance) 
            parser.set(section, "csnakeFile%s" % index, self.__recentlyUsed[index].__csnakeFile) 

    def AddRecentlyUsed(self, _instance, _csnakeFile):
        for item in range( len(self.__recentlyUsed) ):
            x = self.__recentlyUsed[item]
            if (x.__instance == _instance and x.__csnakeFile == _csnakeFile):
                self.__recentlyUsed.remove(x)
                self.__recentlyUsed.insert(0, x)
                return
        
        x = Context()
        (x.__instance, x.__csnakeFile) = (_instance, _csnakeFile)
        self.__recentlyUsed.insert(0, x)
    
    def IsCSnakeFileInRecentlyUsed(self):
        """ Returns True if self.__csnakeFile is in the list of recently used csnake files """
        result = False
        for item in range( len(self.__recentlyUsed) ):
            x = self.__recentlyUsed[item]
            if (x.__csnakeFile == self.__csnakeFile):
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
            field = "_Context__" + basicField
            parser.set(section, basicField, getattr(self, field))
        parser.set(section, "filter", ";".join(self.__filter))
        
        count = 0
        while count < len(self.__rootFolders):
            parser.set(rootFolderSection, "RootFolder%s" % count, self.__rootFolders[count] )
            count += 1

        count = 0
        while count < len(self.__thirdPartySrcAndBuildFolders):
            parser.set(thirdPartyFolderSection, "ThirdPartyFolder%s" % count, self.__thirdPartySrcAndBuildFolders[count][0] )
            parser.set(thirdPartyBuildFolderSection, "ThirdPartyBuildFolder%s" % count, self.__thirdPartySrcAndBuildFolders[count][1] )
            count += 1

        self.__SaveRecentlyUsedCSnakeFiles(parser)
        
        f = open(filename, 'w')
        parser.write(f)
        f.close()

    def SetSuperSubCategory(self, super, sub):
        """ 
        Makes super a supercategory of sub. This information is used to be able to disable all Tests with a single
        click (since Tests will be a supercategory of each Test project).
        """
        if not self.__subCategoriesOf.has_key(super):
            self.__subCategoriesOf[super] = OrderedSet.OrderedSet()
        self.__subCategoriesOf[super].add(sub)
        
    def GetThirdPartyBuildFolderByIndex(self, index):
        # "os.path.join" would be better, but doesn't work in Windows because backslashes are not (yet) escaped by csnake
        return self.__thirdPartySrcAndBuildFolders[index][1] + "/" + self.__compiler.GetThirdPartySubFolder()

    def GetThirdPartyBuildFolders(self):
        result = []
        for srcAndBuildFolder in self.__thirdPartySrcAndBuildFolders:
            result.append(srcAndBuildFolder[1])
        return result
    
    def GetThirdPartyBuildFoldersComplete(self):
        GetThirdPartyBuildFoldersComplete = []
        for srcAndBuildFolder in self.__thirdPartySrcAndBuildFolders:
            GetThirdPartyBuildFoldersComplete.append(srcAndBuildFolder[1] + "/" + self.__compiler.GetThirdPartySubFolder())
        return GetThirdPartyBuildFoldersComplete
    
    def GetThirdPartyFolder(self, index = 0):
        return self.__thirdPartySrcAndBuildFolders[index][0]

    def GetThirdPartyFolders(self):
        result = []
        for srcAndBuildFolder in self.__thirdPartySrcAndBuildFolders:
            result.append(srcAndBuildFolder[0])
        return result

    def GetNumberOfThirdPartyFolders( self ):
        return len(self.__thirdPartySrcAndBuildFolders)
    
    def AddThirdPartySrcAndBuildFolder(self, srcFolder = "", buildFolder = ""):
        self.__thirdPartySrcAndBuildFolders.append([srcFolder, buildFolder])
    
    def RemoveThirdPartySrcAndBuildFolderByIndex(self, index):
        self.__thirdPartySrcAndBuildFolders = self.__thirdPartySrcAndBuildFolders[0:index] + self.__thirdPartySrcAndBuildFolders[index+1:]
    
    def MoveUpThirdPartySrcAndBuildFolder(self, index):
        self.__thirdPartySrcAndBuildFolders = self.__thirdPartySrcAndBuildFolders[0:index-1] + [self.__thirdPartySrcAndBuildFolders[index], self.__thirdPartySrcAndBuildFolders[index-1]] + self.__thirdPartySrcAndBuildFolders[index+1:]
        
    def MoveDownThirdPartySrcAndBuildFolder(self, index):
        self.__thirdPartySrcAndBuildFolders = self.__thirdPartySrcAndBuildFolders[0:index] + [self.__thirdPartySrcAndBuildFolders[index+1], self.__thirdPartySrcAndBuildFolders[index]] + self.__thirdPartySrcAndBuildFolders[index+2:]
        
    def AddRootFolder(self, newRootFolder ):
        
        # Check that the new folder doesn't have the same structure than the old ones
        newRootFolderSubdirs = []
        excludedFolders = ["CVS", ".svn"]
        csnUtility.GetDirs( newRootFolder, newRootFolderSubdirs, excludedFolders )
        for oldRootFolder in self.__rootFolders:
            oldRootFolderSubdirs = []
            csnUtility.GetDirs( oldRootFolder, oldRootFolderSubdirs, excludedFolders )
            for oldSubDir in oldRootFolderSubdirs:
                for newSubDir in newRootFolderSubdirs:
                    if newSubDir == oldSubDir:
                        message = "Error: The new folder (%s) cannot contain similar subfolders than an already set folder (%s)" % (newRootFolder,oldRootFolder)
                        raise Exception( message )
        
        self.__rootFolders.append(newRootFolder)

    
    def FindCompiler(self):
        #print "FindCompiler"
        if self.__compiler is None or self.__compiler.GetName() != self.__compilername:
            #print "FindCompiler: Update"
            self.__compiler = self.__compilermap[self.__compilername]
            self.__compilername = self.__compiler.GetName()
            try:
                path = csnUtility.GetDefaultVisualStudioPath( self.__compilername )
                if self.__idePath != path:
                    self.__idePath = path
            except Exception, message:
                print message
    
    def CreateProject(self, _name, _type, _sourceRootFolder = None, _categories = None):
        project = csnProject.GenericProject(_name, _type, _sourceRootFolder, _categories, _context = self)
        for flag in self.__compiler.GetCompileFlags():
            project.compileManager.private.definitions.append(flag)
        return project
    
    def GetOutputFolder(self, mode):
        # "os.path.join" would be better, but doesn't work in Windows because backslashes are not (yet) escaped by csnake
        return self.__buildFolder + "/" + self.__compiler.GetOutputSubFolder(mode)
    
    #thirdPartyBinFolder = property(GetThirdPartyBuildFolder) # for backward compatibility

import csnKDevelop
import csnVisualStudio2003
import csnVisualStudio2005
import csnVisualStudio2008
        
def Load(filename):
    context = Context()
    okay = context.Load(filename)
    assert okay, "Error loading from %s\n" % filename
    return context
    
