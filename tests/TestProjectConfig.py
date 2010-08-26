import ConfigParser

class TestProjectConfig():
    """ Configuration for a test project (mini context). """
    
    def __init__(self, name, pType, buildMode, 
            rootDirs, binDir, 
            tpSrcDirs, tpBinDirs, 
            csnakeFile,
            newSyntax = False):
        """ Constructor.
        Warning: all paths should be relative to the CSnake/tests/data folder.
        name: the name of the project.
        pType: the type of the project (exe or lib).
        buildMode: the build mode (Debug or Release).
        rootDirs: the root source dirs (array).
        binDir: the binary dir.
        tpSrcDirs: the third party source dirs (array).
        tpBinDirs: the third party binary dirs (array).
        newSyntax: use old syntax for source folders (in this case only the first value of the input
          arrays will be used).
        """
        # set at input
        self.__name = name
        self.__type = pType
        self.__buildMode = buildMode
        self.__rootDirs = rootDirs
        self.__binDir = binDir
        self.__tpSrcDirs = tpSrcDirs
        self.__tpBinDirs = tpBinDirs
        self.__csnakeFile = csnakeFile
        self.__newSyntax = newSyntax
        # internals
        self.__isVisualStudioConfig = None

    # Get inputs
    
    def getName(self):
        return self.__name

    def getType(self):
        return self.__type
    
    def getBuildMode(self):
        return self.__buildMode

    def getRootDirs(self):
        return self.__rootDirs

    def getBinDir(self):
        return self.__binDir

    def getTpSrcDirs(self):
        return self.__tpSrcDirs

    def getTpBinDirs(self):
        return self.__tpBinDirs
    
    def getCsnakeFile(self):
        return self.__csnakeFile
    
    def isNewSyntax(self):
        return self.__newSyntax
    
    # Methods
    
    def getInstanceName(self):
        return self.__name.lower()[0] + self.__name[1:]
    
    def getExeName(self):
        if self.__type == "exe":
            exeName = self.getName()
        # ok, a bit fishy, I know the application name...
        elif self.__type == "lib":
            exeName = self.getName() + "Applications_myApp"
        return exeName

    def getBuildPath(self):
        if self.__type == "exe":
            buildPath = "%s/executable" % self.__binDir
        elif self.__type == "lib":
            buildPath = "%s/library" % self.__binDir
        return buildPath
        
    
    def getTemplateContextFileName(self):
        return "config/csnake_context.txt"
    
    def getContextFileName(self):
        return "config/csnake_context-%s.txt" % self.__name
    
    def isVisualStudioConfig(self):
        """ Is the context for a visual studio configuration. """
        if self.__isVisualStudioConfig == None:
            cf = ConfigParser.ConfigParser()
            cf.read(self.getTemplateContextFileName())
            csnakeSectionName = "CSnake"
            if( cf.get(csnakeSectionName, "compilername").find("Visual Studio") != -1 ):
                self.__isVisualStudioConfig = True
            else:
                self.__isVisualStudioConfig = False
        # default
        return self.__isVisualStudioConfig
        
    def createContext(self):
        # modify the csnake context file
        cf = ConfigParser.ConfigParser()
        cf.read(self.getTemplateContextFileName())
        # sections
        csnakeSectionName = "CSnake"
        rootFoldersSectionName = "RootFolders"
        tpSourceSectionName = "ThirdPartyFolders"
        tpBinSectionName = "ThirdPartyBuildFolders"
        
        # modify: instance
        cf.set(csnakeSectionName, "instance", self.getInstanceName())
        
        # modify: csnake file
        oldValue = cf.get(csnakeSectionName, "csnakefile")
        newValue = oldValue + "/" + self.__csnakeFile
        cf.set(csnakeSectionName, "csnakefile", newValue)
        
        # modify: build mode
        if self.isVisualStudioConfig():
            cf.set(csnakeSectionName, "configurationname", "DebugAndRelease")
        else:
            cf.set(csnakeSectionName, "configurationname", self.__buildMode)
        
        # modify: root folder
        oldValue = cf.get(rootFoldersSectionName, "rootfolder0")
        if self.__newSyntax:
            count = 0
            for srcDir in self.__rootDirs:
                newValue = oldValue + "/" + srcDir
                option = "rootfolder%s" % count
                cf.set(rootFoldersSectionName, option, newValue )
                count += 1
        else:
            newValue = oldValue + "/" + self.__rootDirs[0]
            cf.set(rootFoldersSectionName, "rootfolder0", newValue )
        
        # modify: bin folder
        oldValue = cf.get(csnakeSectionName, "buildfolder")
        newValue = oldValue + "/" + self.__binDir
        cf.set(csnakeSectionName, "buildfolder", newValue )
        
        # modify: third party src folder
        oldValue = cf.get(csnakeSectionName, "thirdpartyrootfolder")
        if self.__newSyntax:
            # remove old option (TODO: not yet working)
            #cf.remove_option(csnakeSectionName, "thirdpartyrootfolder")
            # add new one
            cf.add_section(tpSourceSectionName)
            count = 0
            for srcDir in self.__tpSrcDirs:
                newValue = oldValue + "/" + srcDir
                option = "thirdpartyfolder%s" % count
                cf.set(tpSourceSectionName, option, newValue )
                count += 1
        else:
            newValue = oldValue + "/" + self.__tpSrcDirs[0]
            cf.set(csnakeSectionName, "thirdpartyrootfolder", newValue )
        
        # modify: third party bin folder
        oldValue = cf.get(csnakeSectionName, "thirdpartybuildfolder")
        if self.__newSyntax:
            # remove old syntax (TODO: not yet working)
            #cf.remove_option(csnakeSectionName, "thirdpartybuildfolder")
            # add new one
            cf.add_section(tpBinSectionName)
            count = 0
            for srcDir in self.__tpBinDirs:
                newValue = oldValue + "/" + srcDir
                option = "thirdpartybuildfolder%s" % count
                cf.set(tpBinSectionName, option, newValue )
                count += 1
        else:
            newValue = oldValue + "/" + self.__tpBinDirs[0]
            cf.set(csnakeSectionName, "thirdpartybuildfolder", newValue )
        
        # save the new context file
        contextNewFile = open(self.getContextFileName(), 'w')
        cf.write(contextNewFile)
        contextNewFile.close()
        