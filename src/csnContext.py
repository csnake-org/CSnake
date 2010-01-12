import ConfigParser
import OrderedSet
import re
import csnProject
import os


latestFileFormatVersion = 2.0

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
        self.buildFolder = ""    
        self.installFolder = ""    
        self.prebuiltBinariesFolder = ""    
        self.thirdPartyBuildFolder = ""
        self.csnakeFile = ""
        self.rootFolders = []
        self.thirdPartyRootFolder = ""
        self.instance = ""
        self.testRunnerTemplate = "normalRunner.tpl"
        self.recentlyUsed = list()
        self.filter = ["Demos", "Applications", "Tests"]
        self.configurationName = "DebugAndRelease"
        self.compilername = "Visual Studio 7 .NET 2003"
        self.compiler = None
        self.cmakePath = "CMake"    
        self.subCategoriesOf = dict()
        self.pythonPath = "D:/Python24/python.exe"
        self.idePath = ""
        self.kdevelopProjectFolder = ""
            
        self.basicFields = [
            "buildFolder", "installFolder", "prebuiltBinariesFolder", "thirdPartyBuildFolder", "csnakeFile",
            "thirdPartyRootFolder", "instance", "testRunnerTemplate", "configurationName", "compilername",
            "cmakePath", "pythonPath", "idePath", "kdevelopProjectFolder"
        ]
        
        self.compilermap = {}
        self.RegisterCompiler(csnKDevelop.KDevelop())
        self.RegisterCompiler(csnKDevelop.Makefile())
        self.RegisterCompiler(csnVisualStudio2003.Compiler())
        self.RegisterCompiler(csnVisualStudio2005.Compiler())
        self.RegisterCompiler(csnVisualStudio2005.Compiler64())
        self.RegisterCompiler(csnVisualStudio2008.Compiler())
        self.RegisterCompiler(csnVisualStudio2008.Compiler64())
    
    def RegisterCompiler(self, compiler):
        self.compilermap[compiler.GetName()] = compiler
        compiler.context = self
    
    def LoadCompilerName(self, parser):
        activateOutput = False
        # temporary workaround to support old versions of the context file
        compilerfieldnames = ["compilername", "compiler"]
        for compilerfieldname in compilerfieldnames:
            try:
                if activateOutput:
                    print "Try with \"%s\"" % compilerfieldname
                self.compilername = parser.get("CSnake", compilerfieldname)
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
            self.__LoadRecentlyUsedCSnakeFiles(parser)
            
            # Temporary workaround to support old versions of the context file;
            # later this line as well as the function "LoadCompilerName" can be removed
            self.LoadCompilerName(parser)
            
            self.FindCompiler()
            return 1
        except:
            return 0
        
    def LoadGlobalSettings(self, filename, globalFields = None):
        """
        Loads only global settings from filename.
        globalFields - This list contains the fields that are considered global. If None, a default list is used.
        """
        try:
            parser = ConfigParser.ConfigParser()
            parser.read([filename])
            section = "CSnake"
            if globalFields is None:
                globalFields = ["testRunnerTemplate", "configurationName", "compiler", "cmakePath", "pythonPath", "idePath"]
            for field in globalFields:
                if parser.has_option(section, field):
                    setattr(self, field, parser.get(section, field))
            return 1
        except:
            return 0
        
    def __LoadBasicFields(self, parser):
        section = "CSnake"
        self.filter = re.split(";", parser.get(section, "filter"))
        for basicField in self.basicFields:
            if parser.has_option(section, basicField):
                setattr(self, basicField, parser.get(section, basicField))

    def __LoadRootFolders(self, parser):
        section = "RootFolders"
        count = 0
        self.rootFolders = []
        while parser.has_option(section, "RootFolder%s" % count):
            self.rootFolders.append( parser.get(section, "RootFolder%s" % count) )
            count += 1
        
    def __LoadRecentlyUsedCSnakeFiles(self, parser):
        self.recentlyUsed = []
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
        for index in range(len(self.recentlyUsed)):
            parser.set(section, "instance%s" % index, self.recentlyUsed[index].instance) 
            parser.set(section, "csnakeFile%s" % index, self.recentlyUsed[index].csnakeFile) 

    def AddRecentlyUsed(self, _instance, _csnakeFile):
        for item in range( len(self.recentlyUsed) ):
            x = self.recentlyUsed[item]
            if (x.instance == _instance and x.csnakeFile == _csnakeFile):
                self.recentlyUsed.remove(x)
                self.recentlyUsed.insert(0, x)
                return
        
        x = Context()
        (x.instance, x.csnakeFile) = (_instance, _csnakeFile)
        self.recentlyUsed.insert(0, x)
    
    def IsCSnakeFileInRecentlyUsed(self):
        """ Returns True if self.csnakeFile is in the list of recently used csnake files """
        result = False
        for item in range( len(self.recentlyUsed) ):
            x = self.recentlyUsed[item]
            if (x.csnakeFile == self.csnakeFile):
                result = True
        return result
    
    def Save(self, filename):
        parser = ConfigParser.ConfigParser()
        section = "CSnake"
        parser.add_section(section)
        parser.set(section, "version", str(latestFileFormatVersion))
        rootFolderSection = "RootFolders"
        parser.add_section(rootFolderSection)

        for basicField in self.basicFields:
            parser.set(section, basicField, getattr(self, basicField))
        parser.set(section, "filter", ";".join(self.filter))
        count = 0
        while count < len(self.rootFolders):
            parser.set(rootFolderSection, "RootFolder%s" % count, self.rootFolders[count] )
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
        if not self.subCategoriesOf.has_key(super):
            self.subCategoriesOf[super] = OrderedSet.OrderedSet()
        self.subCategoriesOf[super].add(sub)
        
    def GetThirdPartyBuildFolder(self):
        # "os.path.join" would be better, but doesn't work in Windows because backslashes are not (yet) escaped by csnake
        return self.thirdPartyBuildFolder + "/" + self.compiler.GetThirdPartySubFolder()
    
    def FindCompiler(self):
        #print "FindCompiler"
        if self.compiler is None or self.compiler.GetName() != self.compilername:
            #print "FindCompiler: Update"
            self.compiler = self.compilermap[self.compilername]
            self.compilername = self.compiler.GetName()
    
    def CreateProject(self, _name, _type, _sourceRootFolder = None, _categories = None):
        project = csnProject.GenericProject(_name, _type, _sourceRootFolder, _categories, _context = self)
        for flag in self.compiler.GetCompileFlags():
            project.compileManager.private.definitions.append(flag)
        return project
    
    def GetOutputFolder(self, mode):
        # "os.path.join" would be better, but doesn't work in Windows because backslashes are not (yet) escaped by csnake
        return self.buildFolder + "/" + self.compiler.GetOutputSubFolder(mode)
    
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
    
