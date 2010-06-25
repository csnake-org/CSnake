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
        self._name = name
        self._type = pType
        self._buildMode = buildMode
        self._rootDirs = rootDirs
        self._binDir = binDir
        self._tpSrcDirs = tpSrcDirs
        self._tpBinDirs = tpBinDirs
        self._csnakeFile = csnakeFile
        self._newSyntax = newSyntax
        # internals
        self._isVisualStudioConfig = None

    # Get inputs
    
    def getName(self):
        return self._name

    def getType(self):
        return self._type
    
    def getBuildMode(self):
        return self._buildMode

    def getRootDirs(self):
        return self._rootDirs

    def getBinDir(self):
        return self._binDir

    def getTpSrcDirs(self):
        return self._tpSrcDirs

    def getTpBinDirs(self):
        return self._tpBinDirs
    
    def getCsnakeFile(self):
        return self._csnakeFile
    
    def isNewSyntax(self):
        return self._newSyntax
    
    # Methods
    
    def getInstanceName(self):
        return self._name.lower()[0] + self._name[1:]
    
    def getExeName(self):
        if self._type == "exe":
            exeName = self.getName()
        # ok, a bit fishy, I know the application name...
        elif self._type == "lib":
            exeName = self.getName() + "Applications_myApp"
        return exeName

    def getBuildPath(self):
        if self._type == "exe":
            buildPath = "%s/executable" % self._binDir
        elif self._type == "lib":
            buildPath = "%s/library" % self._binDir
        return buildPath
        
    
    def getTemplateContextFileName(self):
        return "config/csnake_context.txt"
    
    def getContextFileName(self):
        return "config/csnake_context-%s.txt" % self._name
    
    def isVisualStudioConfig(self):
        """ Is the context for a visual studio configuration. """
        if self._isVisualStudioConfig == None:
            cf = ConfigParser.ConfigParser()
            cf.read(self.getTemplateContextFileName())
            csnakeSectionName = "CSnake"
            if( cf.get(csnakeSectionName, "compilername").find("Visual Studio") != -1 ):
                self._isVisualStudioConfig = True
            else:
                self._isVisualStudioConfig = False
        # default
        return self._isVisualStudioConfig
        
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
        newValue = oldValue + "/" + self._csnakeFile
        cf.set(csnakeSectionName, "csnakefile", newValue)
        
        # modify: build mode
        if self.isVisualStudioConfig():
            cf.set(csnakeSectionName, "configurationname", "DebugAndRelease")
        else:
            cf.set(csnakeSectionName, "configurationname", self._buildMode)
        
        # modify: root folder
        oldValue = cf.get(rootFoldersSectionName, "rootfolder0")
        if self._newSyntax:
            count = 0
            for srcDir in self._rootDirs:
                newValue = oldValue + "/" + srcDir
                option = "rootfolder%s" % count
                cf.set(rootFoldersSectionName, option, newValue )
                count += 1
        else:
            newValue = oldValue + "/" + self._rootDirs[0]
            cf.set(rootFoldersSectionName, "rootfolder0", newValue )
        
        # modify: bin folder
        oldValue = cf.get(csnakeSectionName, "buildfolder")
        newValue = oldValue + "/" + self._binDir
        cf.set(csnakeSectionName, "buildfolder", newValue )
        
        # modify: third party src folder
        oldValue = cf.get(csnakeSectionName, "thirdpartyrootfolder")
        if self._newSyntax:
            # remove old option (TODO: not yet working)
            #cf.remove_option(csnakeSectionName, "thirdpartyrootfolder")
            # add new one
            cf.add_section(tpSourceSectionName)
            count = 0
            for srcDir in self._tpSrcDirs:
                newValue = oldValue + "/" + srcDir
                option = "thirdpartyfolder%s" % count
                cf.set(tpSourceSectionName, option, newValue )
                count += 1
        else:
            newValue = oldValue + "/" + self._tpSrcDirs[0]
            cf.set(csnakeSectionName, "thirdpartyrootfolder", newValue )
        
        # modify: third party bin folder
        oldValue = cf.get(csnakeSectionName, "thirdpartybuildfolder")
        if self._newSyntax:
            # remove old syntax (TODO: not yet working)
            #cf.remove_option(csnakeSectionName, "thirdpartybuildfolder")
            # add new one
            cf.add_section(tpBinSectionName)
            count = 0
            for srcDir in self._tpBinDirs:
                newValue = oldValue + "/" + srcDir
                option = "thirdpartybuildfolder%s" % count
                cf.set(tpBinSectionName, option, newValue )
                count += 1
        else:
            newValue = oldValue + "/" + self._tpBinDirs[0]
            cf.set(csnakeSectionName, "thirdpartybuildfolder", newValue )
        
        # save the new context file
        contextNewFile = open(self.getContextFileName(), 'w')
        cf.write(contextNewFile)
        contextNewFile.close()
        