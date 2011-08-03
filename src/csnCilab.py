## @package csnCilab
# Definition of the methods used for project configuration. 
# This should be the only CSnake import in a project configuration.
import csnUtility
import csnProject
import csnBuild
import os.path
import new
import inspect

def LoadThirdPartyModule(_subFolder, _name):
    """ Loads third party module _name from subfolder _subFolder of the third party folder """
    folderList = []
    for thirdPartyFolder in csnProject.globalCurrentContext.GetThirdPartyFolders( ):
        folderList.append( "%s/%s" % (thirdPartyFolder, _subFolder) )
    return csnUtility.LoadModules(folderList, _name)

def AddApplications(_holderProject, _applicationDependenciesList, _modules, _modulesFolder, _pch = "", _holderName=None, _properties = []):
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

def CilabModuleProject(_name, _type, _sourceRootFolder = None):
    if _sourceRootFolder is None:
        filename = csnProject.FindFilename()
        dirname = os.path.dirname(filename)
        _sourceRootFolder = csnUtility.NormalizePath(dirname, _correctCase = False)
    project = csnProject.Project(_name, _type, _sourceRootFolder)
    project.applicationsProject = None
    project.AddLibraryModules = new.instancemethod(AddLibraryModulesMemberFunction, project)
    project.AddApplications = new.instancemethod(AddApplicationsMemberFunction, project)
    return project

def CommandLinePlugin(_name, _holderProject = None):
    """ Create a command line plugin project. """
    _sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(csnProject.FindFilename()))
    
    # command line lib
    projectLibName = "%sLib" % _name
    projectLib = csnProject.Project(projectLibName, "dll", _sourceRootFolder)
    #project = CilabModuleProject(projectName, "dll", _sourceRootFolder)
    projectLib.AddDefinitions(["-Dmain=ModuleEntryPoint"], _private = 1 ) 
    projectLib.installSubFolder = "commandLinePlugins"
    projectLib.CMakeInsertBeforeTarget = new.instancemethod(CreateCMakeCLPPre, projectLib)
    projectLib.CMakeInsertAfterTarget = new.instancemethod(CreateCMakeCLPPost, projectLib)
    
    # command line executable
    projectAppName = _name
    projectApp = csnBuild.Project(projectAppName, "executable", _sourceRootFolder)
    projectApp.AddProjects( [projectLib] )
    projectApp.installSubFolder = "commandLinePlugins"
    # wrapper for shared libraries
    wrapperSourceFile = None
    for thirdParty in csnProject.globalCurrentContext.GetThirdPartyFolders():
        currentWrapperSourceFile = u'%s/SLICER/Slicer3/Applications/CLI/Templates/CommandLineSharedLibraryWrapper.cxx' % thirdParty
        if os.path.isfile(currentWrapperSourceFile):
            wrapperSourceFile = currentWrapperSourceFile
    if wrapperSourceFile is None:
        raise Exception("Could not find Slicer template in your thirdParty folders.")
    projectApp.AddSources( [wrapperSourceFile]  )

    # force the creation of the application project
    projectLib.AddProjects([projectApp], _dependency = 0)
    
    if not (_holderProject is None):
        _holderProject.AddProjects( [projectLib] )
    
    return projectLib

def CreateCMakeCLPPre(self, _file):
    """ CLP Cmake specific, prefix to main cmake section. """
    if len( self.GetSources() ) > 0:
        _file.write("\n# Adding CMake GenerateCLP Pre\n")
        _file.write("SET( CLP ${PROJECT_NAME}CLP )\n" )
        _file.write("SET( ${CLP}_SOURCE \"%s\" )\n" % self.GetSources()[0] )
        _file.write("GET_FILENAME_COMPONENT( TMP_FILENAME ${${CLP}_SOURCE} NAME_WE )\n" )
        _file.write("SET( ${CLP}_INCLUDE_FILE ${CMAKE_CURRENT_BINARY_DIR}/${TMP_FILENAME}CLP.h )\n" )
        self.AddSources( ['${${CLP}_INCLUDE_FILE}'], _checkExists = 0, _forceAdd = 1 )

def CreateCMakeCLPPost(self, _file):
    """ CLP Cmake specific, postfix to main cmake section. """
    if len( self.GetSources() ) > 0:
        _file.write("\n# Adding CMake GenerateCLP Post\n")
        sourceFile = self.GetSources()[0]
        if sourceFile.endswith("cxx"):
            xmlFile = sourceFile.replace( "cxx", "xml" )
        elif sourceFile.endswith("cpp"):
            xmlFile = sourceFile.replace( "cpp", "xml" )
        else:
            raise Exception("Unsupported file extension: %s." % sourceFile)
        # GenerateCLP should be a dependency of the project, no need to find package
        _file.write( "GENERATECLP( ${CLP}_SOURCE \"%s\" )\n" % xmlFile )

def AddLibraryModulesMemberFunction(self, _libModules):
    """ 
    Adds source files (anything matching *.c??) and public include folders to self, using a set of libmodules. 
    It is assumed that the root folder of self has a subfolder called libmodules. The subfolders of libmodules should
    contain a subfolder called src (e.g. for mymodule, this would be libmodules/mymodule/src).
    If the src folder has a subfolder called 'stub', it is also added to the source tree.
    _libModules - a list of subfolders of the libmodules folder that should be 'added' to self.
    """
    # add sources
    sourceRootFolder = self.GetSourceRootFolder()
    includeFileExtensions = csnUtility.GetIncludeFileExtensions()
    sourceFileExtensions = csnUtility.GetSourceFileExtensions()
    for libModule in _libModules:
        for stub in ("/stub", ""):
            srcFolder = "libmodules/%s/src%s" % (libModule, stub)
            srcFolderAbs = "%s/%s" % (sourceRootFolder, srcFolder)
            if( os.path.exists(srcFolderAbs) ):
                self.AddIncludeFolders([srcFolder])
                for extension in sourceFileExtensions:
                    self.AddSources(["%s/*.%s" % (srcFolder, extension)], _checkExists = 0)
                for extension in includeFileExtensions:
                    self.AddSources(["%s/*.%s" % (srcFolder, extension)], _checkExists = 0)
    
    if( len(self.GetSources()) == 0 ):
        dummySource = csnUtility.GetDummyCppFilename()
        self.AddSources([dummySource])
    
    for libModule in _libModules:
        for stub in ("/stub", ""):
            includeFolder = "libmodules/%s/include%s" % (libModule, stub)
            includeFolderAbs = "%s/%s" % (sourceRootFolder, includeFolder)
            if( os.path.exists(includeFolderAbs) ):
                self.AddIncludeFolders([includeFolder])
                for extension in includeFileExtensions:
                    self.AddSources(["%s/*.%s" % (includeFolder, extension)], _checkExists = 0)
        
def AddApplicationsMemberFunction(self, _modules, _pch="", _applicationDependenciesList=None, _holderName=None, _properties = []):
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
    AddApplications(self.applicationsProject, dependencies, _modules, _modulesFolder, _pch, _holderName, _properties)
    
def GimiasPluginProject(_name, _sourceRootFolder = None):
    """
    This class is used to build a plugin coming from the CilabApps/Plugins folder. Use AddWidgetModules to add widget
    modules to the plugin.
    """
    if _sourceRootFolder is None:
        _sourceRootFolder = csnUtility.NormalizePath(os.path.dirname(csnProject.FindFilename()))
    pluginName = "GIMIAS%s" % _name
    project = csnProject.Project(
        _name, 
        _type = "dll", 
        _sourceRootFolder = _sourceRootFolder, 
        _categories = [pluginName]
    )
    project.applicationsProject = None
    project.installSubFolder = "plugins/%s/lib" % _name
    project.AddIncludeFolders(["."])
    project.AddWidgetModules = new.instancemethod(AddWidgetModulesMemberFunction, project)
    project.context.SetSuperSubCategory("Plugins", pluginName)

    # Windows debug
    installFolder = "%s/debug" % project.installSubFolder
    project.installManager.AddFilesToInstall( project.Glob( "plugin.xml" ), installFolder, _debugOnly = 1, _WIN32 = 1 )
    installFolder = installFolder + "/Filters/"
    project.installManager.AddFilesToInstall( project.Glob( "Filters/*.xml" ), installFolder, _debugOnly = 1, _WIN32 = 1 )
    
    # Windows release
    installFolder = "%s/release" % project.installSubFolder
    project.installManager.AddFilesToInstall( project.Glob( "plugin.xml" ), installFolder, _releaseOnly = 1, _WIN32 = 1 )
    installFolder = installFolder + "/Filters/"
    project.installManager.AddFilesToInstall( project.Glob( "Filters/*.xml" ), installFolder, _releaseOnly = 1, _WIN32 = 1 )

    # Linux
    project.installManager.AddFilesToInstall( project.Glob( "plugin.xml" ), project.installSubFolder, _NOT_WIN32 = 1 )
    installFolder = project.installSubFolder + "/Filters"
    project.installManager.AddFilesToInstall( project.Glob( "Filters/*.xml" ), installFolder, _NOT_WIN32 = 1 )
    
    return project

def AddWidgetModulesMemberFunction(self, _widgetModules, _holdingFolder = None, _useQt = 0):
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
            for extension in csnUtility.GetSourceFileExtensions():
                self.AddSources(["%s/*.%s" % (srcFolder, extension)], _checkExists = 0, _sourceGroup = "Widgets")
            if _useQt:
                self.AddSources(["%s/*.ui" % srcFolder], _ui = 1, _checkExists = 0, _sourceGroup = "WidgetsUI")
            
        includeFolder = "%s/%s" % (_holdingFolder, widgetModule)
        includeFolderAbs = "%s/%s" % (self.GetSourceRootFolder(), includeFolder)
        if( os.path.exists(includeFolderAbs) ):
            self.AddIncludeFolders([includeFolder])
            for extension in csnUtility.GetIncludeFileExtensions():
                self.AddSources(["%s/*.%s" % (includeFolder, extension)], _moc = _useQt and extension == "h", _checkExists = 0, _sourceGroup = "Widgets")

def CreateToolkitHeader(project, filename = None, variables = None):
    """ 
    Creates a header file with input vars for the given project.
    @param project The calling project.
    @param filename The header file name (will be created in the projects' build folder), defaults to "CISTIBToolkit.h".
    @param variables Dictionary of variable/value pairs.  
     """
    if not filename: 
        filename = "CISTIBToolkit.h"
    path = "%s/%s" % (project.GetBuildFolder(), filename)
    headerFile = open(path, 'w')
    # simple '.' to '_' replace, if the method is passed we cannot use the string package.
    size = len(filename)
    # should be a header...
    guard = "%s_H" % filename[0:size-2].upper()
    headerFile.write("#ifndef %s\n" % guard)
    headerFile.write("#define %s\n" % guard)
    headerFile.write("\n")
    headerFile.write("// Automatically generated file, do not edit.\n")
    headerFile.write("\n")
    
    # default variables
    headerFile.write("#define CISTIB_TOOLKIT_FOLDER \"%s/..\"\n" % project.GetSourceRootFolder())
    headerFile.write("#define CISTIB_TOOLKIT_BUILD_FOLDER \"%s\"\n" % project.GetBuildFolder())
    
    # input variables
    if variables:
        headerFile.write("\n")
        for (key, value) in variables:
            headerFile.write("#define %s \"%s\"\n" % (key, value))
    
    headerFile.write("\n")
    headerFile.write("#endif // %s\n" % guard)
    headerFile.close()

