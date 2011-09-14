## @package csnCilab
# Definition of the methods used for project configuration. 
# This should be the only CSnake import in a project configuration.
import csnUtility
import csnProject
import csnBuild
import os.path
import inspect
from csnProject import GenericProject

class StandardModuleProject(GenericProject):
    """ GenericProject with applications and modules in specific folders. """

    def __init__(self, _name, _type, _sourceRootFolder = None):
        if _sourceRootFolder is None:
            _sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(inspect.stack()[1][1]))
        GenericProject.__init__(self, _name, _type, _sourceRootFolder)
        self.applicationsProject = None

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
                    for extension in csnUtility.GetSourceFileExtensions():
                        self.AddSources(["%s/*.%s" % (srcFolder, extension)], _checkExists = 0)
                    for extension in csnUtility.GetIncludeFileExtensions():
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
                    for extension in csnUtility.GetIncludeFileExtensions():
                        self.AddSources(["%s/*.%s" % (includeFolder, extension)], _checkExists = 0)
        
    def AddApplications(self, _modules, _pch="", _applicationDependenciesList=None, _holderName=None, _properties = []):
        """
        Creates extra CSnake projects, each project building one application in the 'Applications' subfolder of the current project.
    
        _modules - List of the subfolders within the 'Applications' subfolder that must be scanned for applications.
        _pch - If not "", this is the include file used to generate a precompiled header for each application.
        """
        dependencies = [self]
        if not _applicationDependenciesList is None:
            dependencies.extend(_applicationDependenciesList)
            
        if _holderName is None:
            _holderName = "%sApplications" % self.name
            
        csnProject.globalCurrentContext.SetSuperSubCategory("Applications", _holderName)
        if self.applicationsProject is None:
            self.applicationsProject = csnBuild.Project(self.name + "Applications", "container", _sourceRootFolder = self.GetSourceRootFolder(), _categories = [_holderName])
            #self.applicationsProject.AddSources([csnUtility.GetDummyCppFilename()], _sourceGroup = "CSnakeGeneratedFiles")
            self.applicationsProject.AddProjects([self])
            self.AddProjects([self.applicationsProject], _dependency = 0)
        
        # look for an 'applications' or 'Applications' folder
        _modulesFolder = "%s/applications" % self.GetSourceRootFolder()
        if not os.path.exists(_modulesFolder):
            _modulesFolder = "%s/Applications" % self.GetSourceRootFolder()
        self.__AddApplications(self.applicationsProject, dependencies, _modules, _modulesFolder, _pch, _holderName, _properties)

    def __AddApplications(self, _holderProject, _applicationDependenciesList, _modules, _modulesFolder, _pch = "", _holderName=None, _properties = []):
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
            for extension in csnUtility.GetSourceFileExtensions():
                sourceFiles.extend(_holderProject.Glob("%s/*.%s" % (moduleFolder, extension)))
    
            for extension in csnUtility.GetIncludeFileExtensions():
                headerFiles.extend(_holderProject.Glob("%s/*.%s" % (moduleFolder, extension)))
            
            for sourceFile in sourceFiles:
                if os.path.isdir(sourceFile):
                    continue
                name = os.path.splitext( os.path.basename(sourceFile) )[0]
                name = name.replace(' ', '_')
                if _holderName is None:
                    _holderName = _holderProject.name
                app = csnBuild.Project("%s_%s" % (_holderName, name), "executable", _sourceRootFolder = _holderProject.GetSourceRootFolder())
                app.AddIncludeFolders([moduleFolder]) 
                app.AddProjects(_applicationDependenciesList)
                app.AddSources([sourceFile])
                app.AddProperties( _properties )
                # add header files so that they appear in visual studio
                app.AddSources(headerFiles)
                if( _pch != "" ):
                    app.SetPrecompiledHeader(_pch)
                _holderProject.AddProjects([app])
