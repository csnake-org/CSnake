import csnBuild
import csnUtility
import os.path

thirdPartyModuleFolder = ""
thirdPartyBinFolder = ""
defaultLibType = "dll"

def GetSourceFileExtensions():
    return ["cxx", "cc", "cpp"]
    
def GetIncludeFileExtensions():
    return ["h", "hpp", "txx"]
    
def LoadThirdPartyModule(_subFolder, _name):
    """ Loads third party module _name from subfolder _subFolder of the third party folder """
    assert thirdPartyModuleFolder != ""
    folder = "%s/%s" % (thirdPartyModuleFolder, _subFolder)
    return csnUtility.LoadModule(folder, _name)

def AddApplications(_holderProject, _applicationDependenciesList, _modules, _modulesFolder, _pch = ""):
    """ 
    Creates application projects and adds them to _holderProject (using _holderProject.AddProject). The holder
    project does not depend on these application projects.
    It is assumed that _modules is a list containing subfolders of _modulesFolder.
    Each subfolder in _modules should contain source files (.cpp, .cxx or .cc), where each source file corresponds to a single application.
    Hence, each source file is used to create a new application project. For example, assuming that the _modulesFolder
    is called 'Applications', the file 'Applications/Small/Tiny.cpp' will be used to build the 'Tiny' application.
    
    _applicationDependenciesList - List of projects that each new application project is dependent on.
    _modulesFolder - Folder containing subfolders with applications.
    _modules = List of subfolders of _modulesFolder that should be processed.
    _pch - If not "", this is the C++ include file which is used for building a precompiled header file for each application.
    """
    for module in _modules:
        moduleFolder = "%s/%s" % (_modulesFolder, module)
        sourceFiles = []
        headerFiles = []
        for extension in GetSourceFileExtensions():
            sourceFiles.extend(_holderProject.Glob("%s/*.%s" % (moduleFolder, extension)))

        for extension in GetIncludeFileExtensions():
            headerFiles.extend(_holderProject.Glob("%s/*.%s" % (moduleFolder, extension)))
        
        for sourceFile in sourceFiles:
            if os.path.isdir(sourceFile):
                continue
            (name, ext) = os.path.splitext( os.path.basename(sourceFile) )
            app = csnBuild.Project("%s.%s" % (_holderProject.name, name), "executable", _sourceRootFolder = _holderProject.sourceRootFolder)
            app.AddIncludeFolders([moduleFolder]) 
            app.AddProjects(_applicationDependenciesList)
            app.AddSources([sourceFile])
            # add header files so that they appear in visual studio
            app.AddSources(headerFiles)
            if( _pch != "" ):
                app.SetPrecompiledHeader(_pch)
            _holderProject.AddProjects([app])

        
class CilabModuleProject(csnBuild.Project):
    """
    This class is used to build a library coming from the CilabModules folder. Use AddLibraryModules to create libraries
    from source in the libmodules subfolder of a cilab module. Use AddDemos and AddApplications to add executable projects
    based on sources in the 'demos' and 'Applications' subfolders.
    """
    def __init__(self, _name, _type):
        csnBuild.Project.__init__(self, _name, _type)
        
    def AddLibraryModules(self, _libModules):
        """ 
        Adds source files (anything matching *.c??) and public include folders to self, using a set of libmodules. 
        It is assumed that the root folder of self has a subfolder called libmodules. The subfolders of libmodules should
        contain a subfolder called src (e.g. for mymodule, this would be libmodules/mymodule/src).
        _libModules - a list of subfolders of the libmodules folder that should be 'added' to self.
        """
        # add sources    
        for libModule in _libModules:
            srcFolder = "libmodules/%s/src" % (libModule)
            srcFolderAbs = "%s/%s" % (self.sourceRootFolder, srcFolder)
            if( os.path.exists(srcFolderAbs) ):
                self.AddIncludeFolders([srcFolder])
                for extension in GetSourceFileExtensions():
                    self.AddSources(["%s/*.%s" % (srcFolder, extension)], _checkExists = 0)
                for extension in GetIncludeFileExtensions():
                    self.AddSources(["%s/*.%s" % (srcFolder, extension)], _checkExists = 0)

            if( len(self.sources) == 0 ):
                self.AddSources([csnUtility.GetDummyCppFilename()])
                
            includeFolder = "libmodules/%s/include" % libModule
            includeFolderAbs = "%s/%s" % (self.sourceRootFolder, includeFolder)
            if( os.path.exists(includeFolderAbs) ):
                self.AddIncludeFolders([includeFolder])
                for extension in GetIncludeFileExtensions():
                    self.AddSources(["%s/*.%s" % (includeFolder, extension)], _checkExists = 0)
        
    def AddDemos(self, _modules, _pch = ""):
        """
        Creates extra CSnake projects, each project building one demo in the demos subfolder of the current project.
        _modules - List of the subfolders within the demos subfolder that must be scanned for demos.
        _pch - If not "", this is the include file used to generate a precompiled header for each demo.
        """
        demosProject = csnBuild.Project(self.name + "Demos", "library", _sourceRootFolder = self.sourceRootFolder)
        demosProject.AddSources([csnUtility.GetDummyCppFilename()], _sourceGroup = "CSnakeGeneratedFiles")
        AddApplications(demosProject, [self], _modules, "%s/demos" % self.sourceRootFolder, _pch)
        demosProject.AddProjects([self])
        self.AddProjects([demosProject], _dependency = 0)

    def AddApplications(self, _modules, _pch = ""):
        """
        Similar to AddDemos, but works on the Applications subfolder.
        """
        applicationsProject = csnBuild.Project(self.name + "Applications", "library", _sourceRootFolder = self.sourceRootFolder)
        applicationsProject.AddSources([csnUtility.GetDummyCppFilename()], _sourceGroup = "CSnakeGeneratedFiles")
        AddApplications(applicationsProject, [self], _modules, "%s/Applications" % self.sourceRootFolder, _pch)
        applicationsProject.AddProjects([self])
        self.AddProjects([applicationsProject], _dependency = 0)

class GimiasPluginProject(csnBuild.Project):
    """
    This class is used to build a plugin coming from the CilabApps/Plugins folder. Use AddWidgetModules to add widget
    modules to the plugin.
    """
    def __init__(self, _name):
        csnBuild.Project.__init__(self, _name, "dll")
        self.installSubFolder = "${CMAKE_CFG_INTDIR}/plugins/%s/lib" % _name
        self.AddIncludeFolders(["."])
        
    def AddWidgetModules(self, _widgetModules, _holdingFolder = "widgets", _useQt = 1):
        """ 
        Similar to AddCilabLibraryModules, but this time the source code in the widgets folder is added to self.
        _useQt - If true, adds build rules for the ui and moc files .
        """
        # add sources    
        for widgetModule in _widgetModules:
            srcFolder = "%s/%s" % (_holdingFolder, widgetModule)
            srcFolderAbs = "%s/%s" % (self.sourceRootFolder, srcFolder)
            if( os.path.exists(srcFolderAbs) ):
                self.AddIncludeFolders([srcFolder])
                for extension in GetSourceFileExtensions():
                    self.AddSources(["%s/*.%s" % (srcFolder, extension)], _checkExists = 0, _sourceGroup = "Widgets")
                if _useQt:
                    self.AddSources(["%s/*.ui" % srcFolder], _ui = 1, _checkExists = 0, _sourceGroup = "WidgetsUI")
                
            includeFolder = "%s/%s" % (_holdingFolder, widgetModule)
            includeFolderAbs = "%s/%s" % (self.sourceRootFolder, includeFolder)
            if( os.path.exists(includeFolderAbs) ):
                self.AddIncludeFolders([includeFolder])
                for extension in GetIncludeFileExtensions():
                    self.AddSources(["%s/*.%s" % (includeFolder, extension)], _moc = _useQt and extension == "h", _checkExists = 0, _sourceGroup = "Widgets")
