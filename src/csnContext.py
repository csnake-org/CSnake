import ConfigParser
import OrderedSet
import re

latestFileFormatVersionAsString = "2.0"


class Context:
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
        self.compiler = "Visual Studio 7 .NET 2003"
        self.cmakePath = "CMake"    
        self.subCategoriesOf = dict()
        self.pythonPath = "D:/Python24/python.exe"
        self.idePath = ""
            
        self.basicFields = [
            "buildFolder", "installFolder", "prebuiltBinariesFolder", "thirdPartyBuildFolder", "csnakeFile",
            "thirdPartyRootFolder", "instance", "testRunnerTemplate", "configurationName", "compiler",
            "cmakePath", "pythonPath", "idePath"
        ]
            
    def Load(self, filename):
        try:
            parser = ConfigParser.ConfigParser()
            parser.read([filename])
            self.__LoadBasicFields(parser)
            self.__LoadRootFolders(parser)
            self.__LoadRecentlyUsedCSnakeFiles(parser)
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
        if len(self.recentlyUsed) > 10:
            self.recentlyUsed.pop() 
    
    def Save(self, filename):
        parser = ConfigParser.ConfigParser()
        section = "CSnake"
        parser.add_section(section)
        parser.set(section, "version", latestFileFormatVersionAsString)
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

import csnKDevelop
import csnVisualStudio2003
import csnVisualStudio2005
import csnVisualStudio2008
        
def Load(filename):
    parser = ConfigParser.ConfigParser()
    parser.read([filename])
    compiler = parser.get("CSnake", "compiler")
    context = None
    if compiler in ("KDevelop3", "Unix Makefiles"):
        context = csnKDevelop.Context()
    elif compiler == "Visual Studio 7 .NET 2003":
        context = csnVisualStudio2003.Context()
    elif compiler in ("Visual Studio 8 2005", "Visual Studio 8 2005 Win64"):
        context = csnVisualStudio2005.Context()
    elif compiler in ("Visual Studio 9 2008", "Visual Studio 9 2008 Win64"):
        context = csnVisualStudio2008.Context()
    else:
        assert False, "\n\nError: Unknown compiler %s in context %s\n" % (compiler, filename)
        
    okay = context.Load(filename)
    assert okay, "Error loading from %s\n" % filename
    return context
