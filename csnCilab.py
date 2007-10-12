import csnBuild
import csnUtility
import os.path

def LoadThirdPartyModule(_subFolder, _name):
    """ Loads third party module _name from subfolder _subFolder of the third party folder """
    folder = "D:\\Users\\Maarten\\Code\\ThirdParty\\thirdParty\\%s" % (_subFolder)
    return csnUtility.LoadModule(folder, _name)

def AddCilabLibraryModules(_project, _libModules):
    """ 
    Creates _project from a set of libmodules. Used to build libraries in CilabModules.
    It is assumed that _libModules is a list of subfolders of the _project.sourceRootFolder/libmodules folder.
    All sources files in these subfolders are added to _project,
    """
    # add sources    
    for libModule in _libModules:
        srcFolder = "libmodules/%s/src" % (libModule)
        srcFolderAbs = "%s/%s" % (_project.sourceRootFolder, srcFolder)
        if( os.path.exists(srcFolderAbs) ):
            _project.AddPublicIncludeFolders([srcFolder])
            _project.AddSources(["%s/*.c??" % srcFolder], _checkExists = 0)
        if( len(_project.sources) == 0 ):
            _project.AddSources([csnUtility.GetDummyCppFilename()])
            
        includeFolder = "libmodules/%s/include" % libModule
        includeFolderAbs = "%s/%s" % (_project.sourceRootFolder, includeFolder)
        if( os.path.exists(includeFolderAbs) ):
            _project.AddPublicIncludeFolders([includeFolder])
            _project.AddSources(["%s/*.h" % includeFolder], _checkExists = 0)

def AddCilabWidgetModules(_project, _widgetModules):
    """ 
    Creates _project from a set of widget modules. Used to build widget libraries for GIMIAS plugins.
    It is assumed that _widgetModules is a list of subfolders of the _project.sourceRootFolder/widgets folder.
    All sources files in these subfolders are added to _project,
    """
    # add sources    
    for widgetModule in _widgetModules:
        srcFolder = "widgets/%s" % (widgetModule)
        srcFolderAbs = "%s/%s" % (_project.sourceRootFolder, srcFolder)
        if( os.path.exists(srcFolderAbs) ):
            _project.AddPublicIncludeFolders([srcFolder])
            _project.AddSources(["%s/*.c??" % srcFolder], _checkExists = 0)
            _project.AddSources(["%s/*.ui" % srcFolder], _ui = 1, _checkExists = 0)
            
        includeFolder = "widgets/%s" % widgetModule
        includeFolderAbs = "%s/%s" % (_project.sourceRootFolder, includeFolder)
        if( os.path.exists(includeFolderAbs) ):
            _project.AddPublicIncludeFolders([includeFolder])
            _project.AddSources(["%s/*.h" % includeFolder], _moc = 1, _checkExists = 0)
            
def AddApplications(_holderProject, _applicationDependenciesList, _modules, _modulesFolder):
    """ 
    Creates application projects from _modulesFolder and adds them to _holderProject.
    It is assumed that _modules is a list containing subfolders of _modulesFolder.
    Each subfolder in _modules should contain source files (.cpp, .cxx or .cc), where each source file corresponds to a single application.
    Hence, each source file is used to create a new application project. This application project is added to _holderProject,
    using _holderProject.AddProject.
    _applicationDependenciesList - List of projects that each new application project is dependent on.
    """
    for module in _modules:
        moduleFolder = "%s/%s" % (_modulesFolder, module)
        sourceFiles = _holderProject.Glob("%s/*.cpp" % (moduleFolder))
        sourceFiles.extend(_holderProject.Glob("%s/*.cxx" % (moduleFolder)))
        sourceFiles.extend(_holderProject.Glob("%s/*.cc" % (moduleFolder)))
        
        for sourceFile in sourceFiles:
            if os.path.isdir(sourceFile):
                continue
            (name, ext) = os.path.splitext( os.path.basename(sourceFile) )
            app = csnBuild.Project("%s.%s" % (_holderProject.name, name), "executable", 2)
            app.AddPublicIncludeFolders([moduleFolder]) 
            app.AddProjects(_applicationDependenciesList)
            app.AddSources([sourceFile])
            _holderProject.AddProjects([app])

class CilabModuleProject(csnBuild.Project):
    """
    This class is used to build a library coming from the CilabModules folder. Use AddLibraryModules to create libraries
    from source in the libmodules subfolder of a cilab module. Use AddDemos and AddApplications to add executable projects
    based on sources in the 'demos' and 'Applications' subfolders.
    """
    def __init__(self, _name, _type, _callerDepth = 1):
        csnBuild.Project.__init__(self, _name, _type, _callerDepth + 1)
        
    def AddLibraryModules(self, _libModules):
        AddCilabLibraryModules(self, _libModules)
        
    def AddDemos(self, _modules):
        demosProject = csnBuild.Project(self.name + "Demos", "library")
        demosProject.AddSources([csnUtility.GetDummyCppFilename()])
        AddApplications(demosProject, [self], _modules, "%s/demos" % self.sourceRootFolder)
        demosProject.AddProjects([self])
        self.AddProjects([demosProject], _dependency = 0)

    def AddApplications(self, _modules):
        applicationsProject = csnBuild.Project(self.name + "Applications", "library")
        applicationsProject.AddSources([csnUtility.GetDummyCppFilename()])
        AddApplications(applicationsProject, [self], _modules, "%s/Applications" % self.sourceRootFolder)
        applicationsProject.AddProjects([self])
        self.AddProjects([applicationsProject], _dependency = 0)

class GimiasPluginProject(csnBuild.Project):
    """
    This class is used to build a library coming from the CilabModules folder. Use AddLibraryModules to create libraries
    from source in the libmodules subfolder of a cilab module. Use AddDemos and AddApplications to add executable projects
    based on sources in the 'demos' and 'Applications' subfolders.
    """
    def __init__(self, _name, _callerDepth = 1):
        csnBuild.Project.__init__(self, _name, "dll", _callerDepth + 1)
        self.widgetProject = csnBuild.Project(self.name + "_Widgets", "library", _callerDepth + 1)
        
    def AddWidgetModules(self, _widgetModules, _dependencyProjects, _dependOnWidgetProject = 1):
        """
        Creates new widget project and adds _widgetModules to the widget project.
        Adds the new widget project to this project.
        _dependencyProjects - List of projects that the widgets project should depend on.
        _dependOnWidgetProject - If true, then the widget project is a dependency project of this project.
        """
        AddCilabWidgetModules(self.widgetProject, _widgetModules)
        self.widgetProject.AddProjects(_dependencyProjects)
        self.AddProjects([self.widgetProject], _dependency = _dependOnWidgetProject)
