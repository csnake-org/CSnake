import csnBuild
import csnUtility
import csnProject
import os.path
import new
import inspect

def GetSourceFileExtensions():
    return ["cxx", "cc", "cpp"]
    
def GetIncludeFileExtensions():
    return ["h", "hpp", "txx"]
    
def LoadThirdPartyModule(_subFolder, _name):
    """ Loads third party module _name from subfolder _subFolder of the third party folder """
    folder = "%s/%s" % (csnProject.globalCurrentContext.thirdPartyRootFolder, _subFolder)
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
            name = os.path.splitext( os.path.basename(sourceFile) )[0]
            name = name.replace(' ', '_')
            app = csnBuild.Project("%s_%s" % (_holderProject.name, name), "executable", _sourceRootFolder = _holderProject.GetSourceRootFolder())
            app.AddIncludeFolders([moduleFolder]) 
            app.AddProjects(_applicationDependenciesList)
            app.AddSources([sourceFile])
            # add header files so that they appear in visual studio
            app.AddSources(headerFiles)
            if( _pch != "" ):
                app.SetPrecompiledHeader(_pch)
            _holderProject.AddProjects([app])

class CilabModuleProject(csnProject.GenericProject):
    def __init__(self, _name, _type, _sourceRootFolder = None):
        self.applicationsProject = None
        self.demosProject = None
        
        if _sourceRootFolder is None:
            _sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(inspect.stack()[1][1]))
        csnProject.GenericProject.__init__(
            self, 
            _name, 
            _type, 
            _sourceRootFolder, 
            _categories = None, 
            _context = csnProject.globalCurrentContext
        )

    def AddLibraryModules(self, _libModules):
        """ 
        Adds source files (anything matching *.c??) and public include folders to self, using a set of libmodules. 
        It is assumed that the root folder of self has a subfolder called libmodules. The subfolders of libmodules should
        contain a subfolder called src (e.g. for mymodule, this would be libmodules/mymodule/src).
        If the src folder has a subfolder called 'stub', it is also added to the source tree.
        _libModules - a list of subfolders of the libmodules folder that should be 'added' to self.
        """
        # add sources    
        for libModule in _libModules:
            for stub in ("/stub", ""):
                srcFolder = "libmodules/%s/src%s" % (libModule, stub)
                srcFolderAbs = "%s/%s" % (self.GetSourceRootFolder(), srcFolder)
                if( os.path.exists(srcFolderAbs) ):
                    self.AddIncludeFolders([srcFolder])
                    for extension in GetSourceFileExtensions():
                        self.AddSources(["%s/*.%s" % (srcFolder, extension)], _checkExists = 0)
                    for extension in GetIncludeFileExtensions():
                        self.AddSources(["%s/*.%s" % (srcFolder, extension)], _checkExists = 0)

        if( len(self.GetSources()) == 0 ):
            dummySource = csnUtility.GetDummyCppFilename()
            self.AddSources([dummySource])

        for libModule in _libModules:
            for stub in ("/stub", ""):
                includeFolder = "libmodules/%s/include%s" % (libModule, stub)
                includeFolderAbs = "%s/%s" % (self.GetSourceRootFolder(), includeFolder)
                if( os.path.exists(includeFolderAbs) ):
                    self.AddIncludeFolders([includeFolder])
                    for extension in GetIncludeFileExtensions():
                        self.AddSources(["%s/*.%s" % (includeFolder, extension)], _checkExists = 0)
        
    def AddDemos(self, _modules, _pch = "", _applicationDependenciesList = None):
        """
        Creates extra CSnake projects, each project building one demo in the demos subfolder of the current project.
        _modules - List of the subfolders within the demos subfolder that must be scanned for demos.
        _pch - If not "", this is the include file used to generate a precompiled header for each demo.
        """
        dependencies = [self]
        if not _applicationDependenciesList is None:
            dependencies.extend(_applicationDependenciesList)

        demosName = "%sDemos" % self.name
        csnProject.globalCurrentContext.SetSuperSubCategory("Demos", demosName)
        if self.demosProject is None:
            self.demosProject = csnBuild.Project(demosName, "dll", _sourceRootFolder = self.GetSourceRootFolder(), _categories = [demosName])
            self.demosProject.AddSources([csnUtility.GetDummyCppFilename()], _sourceGroup = "CSnakeGeneratedFiles")
            self.demosProject.AddProjects([self])
            self.AddProjects([self.demosProject], _dependency = 0)
        AddApplications(self.demosProject, dependencies, _modules, "%s/demos" % self.GetSourceRootFolder(), _pch)

    def AddApplications(self, _modules, _pch = "", _applicationDependenciesList = None):
        """
        Similar to AddDemos, but works on the Applications subfolder.
        """
        dependencies = [self]
        if not _applicationDependenciesList is None:
            dependencies.extend(_applicationDependenciesList)
            
        applicationsName = "%sApplications" % self.name
        csnProject.globalCurrentContext.SetSuperSubCategory("Applications", applicationsName)
        if self.applicationsProject is None:
            self.applicationsProject = csnBuild.Project(self.name + "Applications", "dll", _sourceRootFolder = self.GetSourceRootFolder(), _categories = [applicationsName])
            self.applicationsProject.AddSources([csnUtility.GetDummyCppFilename()], _sourceGroup = "CSnakeGeneratedFiles")
            self.applicationsProject.AddProjects([self])
            self.AddProjects([self.applicationsProject], _dependency = 0)
        AddApplications(self.applicationsProject, dependencies, _modules, "%s/Applications" % self.GetSourceRootFolder(), _pch)
    
class GimiasPluginProject(csnProject.GenericProject):
    """
    This class is used to build a plugin coming from the CilabApps/Plugins folder. Use AddWidgetModules to add widget
    modules to the plugin.
    """
    def __init__(self, _name, _sourceRootFolder = None):
        if _sourceRootFolder is None:
            _sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(inspect.stack()[1][1]))
        csnProject.GenericProject.__init__(
            self, 
            _name, 
            _type = "dll", 
            _sourceRootFolder = _sourceRootFolder, 
            _categories = ["GIMIAS%s" % _name],
            _context = csnProject.globalCurrentContext
        )
        self.installSubFolder = "plugins/%s/lib" % _name
        self.AddIncludeFolders(["."])

    def AddWidgetModules(self, _widgetModules, _holdingFolder = None, _useQt = 0):
        """ 
        Similar to AddCilabLibraryModules, but this time the source code in the widgets folder is added to self.
        _useQt - If true, adds build rules for the ui and moc files .
        """
        
        if _holdingFolder is None:
            _holdingFolder = "widgets"
            
        # add sources    
        for widgetModule in _widgetModules:
            srcFolder = "%s/%s" % (_holdingFolder, widgetModule)
            srcFolderAbs = "%s/%s" % (self.GetSourceRootFolder(), srcFolder)
            if( os.path.exists(srcFolderAbs) ):
                self.AddIncludeFolders([srcFolder])
                for extension in GetSourceFileExtensions():
                    self.AddSources(["%s/*.%s" % (srcFolder, extension)], _checkExists = 0, _sourceGroup = "Widgets")
                if _useQt:
                    self.AddSources(["%s/*.ui" % srcFolder], _ui = 1, _checkExists = 0, _sourceGroup = "WidgetsUI")
                
            includeFolder = "%s/%s" % (_holdingFolder, widgetModule)
            includeFolderAbs = "%s/%s" % (self.GetSourceRootFolder(), includeFolder)
            if( os.path.exists(includeFolderAbs) ):
                self.AddIncludeFolders([includeFolder])
                for extension in GetIncludeFileExtensions():
                    self.AddSources(["%s/*.%s" % (includeFolder, extension)], _moc = _useQt and extension == "h", _checkExists = 0, _sourceGroup = "Widgets")
