import csnBuild
import csnUtility
import os.path

thirdPartyModuleFolder = ""
thirdPartyBinFolder = ""
defaultLibType = "dll"

def LoadThirdPartyModule(_subFolder, _name):
    """ Loads third party module _name from subfolder _subFolder of the third party folder """
    assert thirdPartyModuleFolder != ""
    folder = "%s\\%s" % (thirdPartyModuleFolder, _subFolder)
    return csnUtility.LoadModule(folder, _name)

def AddCilabLibraryModules(_project, _libModules):
    """ 
    Adds source files (anything matching *.c??) and public include folders to _project, using a set of libmodules. 
    It is assumed that the root folder of _project has a subfolder called libmodules. The subfolders of libmodules should
    contain a subfolder called src (e.g. for mymodule, this would be libmodules/mymodule/src).
    _libModules - a list of subfolders of the libmodules folder that should be 'added' to _project.
    """
    # add sources    
    for libModule in _libModules:
        srcFolder = "libmodules/%s/src" % (libModule)
        srcFolderAbs = "%s/%s" % (_project.sourceRootFolder, srcFolder)
        if( os.path.exists(srcFolderAbs) ):
            _project.AddPublicIncludeFolders([srcFolder])
            _project.AddSources(["%s/*.c??" % srcFolder], _checkExists = 0)
            _project.AddSources(["%s/*.h" % srcFolder], _checkExists = 0)
            _project.AddSources(["%s/*.hpp" % srcFolder], _checkExists = 0)
        if( len(_project.sources) == 0 ):
            _project.AddSources([csnUtility.GetDummyCppFilename()])
            
        includeFolder = "libmodules/%s/include" % libModule
        includeFolderAbs = "%s/%s" % (_project.sourceRootFolder, includeFolder)
        if( os.path.exists(includeFolderAbs) ):
            _project.AddPublicIncludeFolders([includeFolder])
            _project.AddSources(["%s/*.h" % includeFolder], _checkExists = 0)

def AddCilabWidgetModules(_project, _widgetModules):
    """ 
    Similar to AddCilabLibraryModules, but this time the source code in the widgets folder is added to _project.
    Also adds rules for qt's ui and moc executables.
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
    Creates application projects and adds them to _holderProject (using _holderProject.AddProject). The holder
    project does not depend on these application projects.
    It is assumed that _modules is a list containing subfolders of _modulesFolder.
    Each subfolder in _modules should contain source files (.cpp, .cxx or .cc), where each source file corresponds to a single application.
    Hence, each source file is used to create a new application project. For example, assuming that the _modulesFolder
    is called 'Applications', the file 'Applications/Small/Tiny.cpp' will be used to build the 'Tiny' application.
    
    _applicationDependenciesList - List of projects that each new application project is dependent on.
    _modulesFolder - Folder containing subfolders with applications.
    _modules = List of subfolders of _modulesFolder that should be processed.
    """
    for module in _modules:
        moduleFolder = "%s/%s" % (_modulesFolder, module)
        sourceFiles = _holderProject.Glob("%s/*.cpp" % (moduleFolder))
        sourceFiles.extend(_holderProject.Glob("%s/*.cxx" % (moduleFolder)))
        sourceFiles.extend(_holderProject.Glob("%s/*.cc" % (moduleFolder)))
        headerFiles = _holderProject.Glob("%s/*.h" % (moduleFolder))
        
        for sourceFile in sourceFiles:
            if os.path.isdir(sourceFile):
                continue
            (name, ext) = os.path.splitext( os.path.basename(sourceFile) )
            app = csnBuild.Project("%s.%s" % (_holderProject.name, name), "executable", _sourceRootFolder = _holderProject.sourceRootFolder)
            app.AddPublicIncludeFolders([moduleFolder]) 
            app.AddProjects(_applicationDependenciesList)
            app.AddSources([sourceFile])
            # add header files so that they appear in visual studio
            app.AddSources(headerFiles)
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
        AddCilabLibraryModules(self, _libModules)
        
    def AddDemos(self, _modules):
        demosProject = csnBuild.Project(self.name + "Demos", "library", _sourceRootFolder = self.sourceRootFolder)
        demosProject.AddSources([csnUtility.GetDummyCppFilename()])
        AddApplications(demosProject, [self], _modules, "%s/demos" % self.sourceRootFolder)
        demosProject.AddProjects([self])
        self.AddProjects([demosProject], _dependency = 0)

    def AddApplications(self, _modules):
        applicationsProject = csnBuild.Project(self.name + "Applications", "library", _sourceRootFolder = self.sourceRootFolder)
        applicationsProject.AddSources([csnUtility.GetDummyCppFilename()])
        AddApplications(applicationsProject, [self], _modules, "%s/Applications" % self.sourceRootFolder)
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
        self.AddPublicIncludeFolders(["."])
        
    def AddWidgetModules(self, _widgetModules):
        """
        Adds _widgetModules to this project.
        """
        AddCilabWidgetModules(self, _widgetModules)
