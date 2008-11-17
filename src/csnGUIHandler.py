import os
import subprocess
import sys
import shutil
import csnUtility
import csnBuild
import csnCilab
import csnVisualStudio2003
import csnVisualStudio2005
import csnKDevelop
import csnPrebuilt
import glob
import RollbackImporter
import inspect
import string

class RootNotFound(IOError):
    pass

class NotARoot(IOError):
    pass

class TypeError(StandardError):
    pass
    
def CreateCSnakeFolder(_folder, _projectRoot):
    # check that project root exists
    if not os.path.exists(_projectRoot):
        raise RootNotFound, "Root folder %s not found." % (_projectRoot)

    # check that project root is a root of _folder
    if( len(os.path.commonprefix([_folder, _projectRoot])) != len(_projectRoot) ):
        raise NotARoot, "%s is is not a root for %s" % (_folder, _projectRoot)
        
    # create _folder, and create __init__.py files in the subtree between _projectRoot and _folder
    os.path.exists(_folder) or os.makedirs(_folder)
    while not os.path.normpath(_folder) == os.path.normpath(_projectRoot):
        initFile = "%s/__init__.py" % (_folder)
        if not os.path.exists(initFile):
            f = open(initFile, 'w')
            f.write( "# Do not remove. Used to find python packages.\n" )
            f.close()
        _folder = os.path.dirname(_folder)

def CreateCSnakeProject(_folder, _projectRoot, _name, _type):
    """ 
    _name - name of the project (e.g. TestLib)
    _type - should be 'executable', 'dll', or 'library' 
    """
    types = ['executable', 'dll', 'library']
    if not _type in types:
        raise TypeError, "Type should be 'executable', 'dll' or 'library'"
        
    CreateCSnakeFolder(_folder, _projectRoot)
    
    nameList = list(_name)
    instanceName = nameList[0].lower() + ''.join(nameList[1:])
    filename = "%s/csn%s.py" % (_folder, _name)
    
    if os.path.exists(filename):
        raise IOError, "Project file %s already exists\n" % (filename)
        
    f = open(filename, 'w')
    f.write( "# Used to configure %s\n" % (_name) )
    f.write( "import csnBuild\n" )
    f.write( "%s = csnBuild.Project(\"%s\", \"%s\")\n" % (instanceName, _name, _type) )
    f.write( "%s.AddSources([\"src/*.h\", \"src/*.cpp\"]) # note: argument must be a python list!\n" % (instanceName) )
    f.write( "%s.AddIncludeFolders([\"src\"]) # note: argument must be a python list!\n" % (instanceName) )
    f.close()

class RollbackHandler:
    """
    This helper class instantiates the RollbackImporter and extends the python search path 
    """
    def SetUp(self, _projectPath, _sourceRootFolders, _thirdPartyRootFolder):
        """
        Set up the roll back. 
        """
        # set up roll back of imported modules
        self.rbi = RollbackImporter.RollbackImporter()
        self.previousPaths = list(sys.path)
        
        # extend python path with project folder, source root and third party root
        newPaths = list(_sourceRootFolders)
        newPaths.extend([_projectPath, _thirdPartyRootFolder]) 
        for path in newPaths:
            if not path in sys.path:
                sys.path.append(path)
    
    def TearDown(self):
        """
        Execute roll back. 
        """
        # roll back imported modules
        self.rbi.rollbackImports()

        # undo additions to the python path
        sys.path = list(self.previousPaths)
                    
class Handler:
    def __init__(self):
        self.cmakePath = ""
        self.pythonPath = ""
        self.cmakeFound = 0 
        self.options = 0
        pass
    
    def SetOptions(self, _options):
        # Set options described by csnGUIOptions.Options
        self.options = _options
        self.SetCompiler(_options.compiler)
        self.SetPythonPath(_options.pythonPath)
        return self.SetCMakePath(_options.cmakePath)
    
    def SetCMakePath(self, _cmakePath):
        if not self.cmakePath == _cmakePath:
            self.cmakePath = _cmakePath
            self.cmakeFound = self.CMakeIsFound() 
            if self.cmakeFound:
                print "CMake was found.\n"
        if not self.cmakeFound:
            print "Warning: %s is is not a valid path to cmake. Select path to CMake using menu Settings->Edit Settings." % self.cmakePath
        return self.cmakeFound
        
    def SetPythonPath(self, path):
        csnBuild.globalSettings.pythonPath = path
        if not (os.path.exists(csnBuild.globalSettings.pythonPath) and os.path.isfile(csnBuild.globalSettings.pythonPath)):
            print "Warning: python not found at: %s. Check the path in the Options menu.\n" % csnBuild.globalSettings.pythonPath
        
        return 1
        
    def SetCompiler(self, _compiler):
        self.compiler = _compiler
        
    def __GetProjectInstance(self, _settings):
        """ Instantiates and returns the _instance in _projectPath. """
        csnBuild.globalSettings.filter = _settings.filter
        csnBuild.globalSettings.testRunnerTemplate = _settings.testRunnerTemplate
        self.DeletePycFiles(_settings)
        
        # set up roll back of imported modules
        rollbackHandler = RollbackHandler()
        rollbackHandler.SetUp(_settings.csnakeFile, _settings.rootFolders, _settings.thirdPartyRootFolder)
        
        csnCilab.thirdPartyModuleFolder = _settings.thirdPartyRootFolder
        csnCilab.thirdPartyBinFolder = _settings.thirdPartyBinFolder
        
        (projectFolder, name) = os.path.split(_settings.csnakeFile)
        (name, ext) = os.path.splitext(name)
        
        try:
            if self.compiler in ("KDevelop3", "Unix Makefiles"):
                csnBuild.globalSettings.compilerType = csnKDevelop.Compiler
            elif self.compiler == "Visual Studio 7 .NET 2003":
                csnBuild.globalSettings.compilerType = csnVisualStudio2003.Compiler
            elif self.compiler in ("Visual Studio 8 2005", "Visual Studio 8 2005 Win64"):
                csnBuild.globalSettings.compilerType = csnVisualStudio2005.Compiler
            else:
                assert false, "\n\nError: Unknown compiler %s\n" % self.compiler
                
            project = csnUtility.LoadModule(projectFolder, name)
            exec "instance = csnBuild.ToProject(project.%s)" % _settings.instance
        finally:
            # undo additions to the python path
            rollbackHandler.TearDown()

        instance.compiler.SetBuildFolder(_settings.buildFolder)
        relocator = csnPrebuilt.ProjectRelocator()
        relocator.Do(instance, _settings.prebuiltBinariesFolder)
        
        self.UpdateRecentlyUsedCSnakeFiles(_settings)
        return instance
    
    def ConfigureProjectToBinFolder(self, _settings, _alsoRunCMake):
        """ 
        Configures the project to the bin folder.
        """
        logString = ""
        instance = self.__GetProjectInstance(_settings)

        generator = csnBuild.Generator(_settings)
        instance.ResolvePathsOfFilesToInstall(_settings.thirdPartyBinFolder)
        
        # on linux, cmake build type DebugAndRelease means that two config steps are performed, for debug and for release
        if self.compiler in ("KDevelop3", "Unix Makefiles") and self.options.cmakeBuildType == "DebugAndRelease":
            generator.Generate(instance, "Debug")
            generator.Generate(instance, "Release")
        else:
            generator.Generate(instance, self.options.cmakeBuildType)
        instance.WriteDependencyStructureToXML("%s/projectStructure.xml" % instance.GetBuildFolder())
            
        if _alsoRunCMake:
            if not self.cmakeFound:
                print "Please specify correct path to CMake"
                return False
                
            argList = [self.cmakePath, "-G", self.compiler, instance.GetCMakeListsFilename()]
            retcode = subprocess.Popen(argList, cwd = _settings.buildFolder).wait()
            if retcode == 0:
                generator.PostProcess(instance)
                return True
            else:
                print "Configuration failed.\n"   
                return False
            
    def InstallBinariesToBinFolder(self, _settings):
        """ 
        This function copies all third party dlls to the binary folder, so that you can run the executables in the
        binary folder without having to build the INSTALL target.
        """
        result = True
        instance = self.__GetProjectInstance(_settings)
        instance.ResolvePathsOfFilesToInstall(_settings.thirdPartyBinFolder)
        
        for mode in ("Debug", "Release"):
            outputFolder = instance.compiler.GetOutputFolder(mode)
            os.path.exists(outputFolder) or os.makedirs(outputFolder)
            for project in instance.GetProjects(_recursive = 1, _includeSelf = True):
                for location in project.filesToInstall[mode].keys():
                    for file in project.filesToInstall[mode][location]:
                        absLocation = "%s/%s" % (outputFolder, location)
                        assert not os.path.isdir(file), "\n\nError: InstallBinariesToBinFolder cannot install a folder (%s)" % file
                        os.path.exists(absLocation) or os.makedirs(absLocation)
                        assert os.path.exists(absLocation), "Could not create %s\n" % absLocation
                        result = (0 != shutil.copy(file, absLocation)) and result
                        #print "Copied %s to %s\n" % (file, absLocation)
        
        return result
             
    def CMakeIsFound(self):
        found = os.path.exists(self.cmakePath) and os.path.isfile(self.cmakePath)
        if not found:
            try:
                retcode = subprocess.Popen(self.cmakePath).wait()
            except:
                retcode = 1
            found = retcode == 0
        return found
    
    def ConfigureThirdPartyFolder(self, _settings, _nrOfTimes = 2):
        """ 
        Runs cmake to install the libraries in the third party folder.
        By default, the third party folder is configured twice because this works around
        some problems with incomplete configurations.
        """
        if not self.cmakeFound:
            print "Please specify correct path to CMake"
            return False
        
        result = True
        os.path.exists(_settings.thirdPartyBinFolder) or os.makedirs(_settings.thirdPartyBinFolder)
        argList = [self.cmakePath, "-G", self.compiler, _settings.thirdPartyRootFolder]
        for i in range(0, _nrOfTimes):
            result = result and 0 == subprocess.Popen(argList, cwd = _settings.thirdPartyBinFolder).wait() 

    	if not result:
                print "Configuration failed.\n"   
            
        return result

    def DeletePycFiles(self, _settings):
        """
        Tries to delete all pyc files from _projectPath, _sourceRootFolders and thirdPartyRootFolder.
        However, __init__.pyc files are not removed.
        """
        # determine list of folders to search for pyc files
        folderList = [_settings.thirdPartyRootFolder]
        folderList.extend(_settings.rootFolders)
                    
        # remove pyc files
        while len(folderList) > 0:
            newFolders = []
            for folder in folderList:
                pycFiles = [x.replace("\\", "/") for x in glob.glob("%s/*.pyc" % folder)]
                for pycFile in pycFiles:
                    if not os.path.basename(pycFile) == "__init__.pyc":
                        os.remove(pycFile)

                newFolders.extend( [os.path.dirname(x).replace("\\", "/") for x in glob.glob("%s/*/__init__.py" % folder)] )
            folderList = list(newFolders)
        
    def GetListOfPossibleTargets(self, _settings):
        """
        Returns a list of possible targets which are defined in CSnake file _projectPath.
        """

        self.DeletePycFiles(_settings)
                
        rollbackHandler = RollbackHandler()
        rollbackHandler.SetUp(_settings.csnakeFile, _settings.rootFolders, _settings.thirdPartyRootFolder)
        result = []

        # find csnake targets in the loaded module
        (projectFolder, name) = os.path.split(_settings.csnakeFile)
        (name, ext) = os.path.splitext(name)
        csnCilab.thirdPartyModuleFolder = _settings.thirdPartyRootFolder
        project = csnUtility.LoadModule(projectFolder, name)   
        for member in inspect.getmembers(project):
            if isinstance(member[1], csnBuild.Project):
                result.append(member[0])
        
        rollbackHandler.TearDown()
        return result
        
    def GetListOfSpuriousPluginDlls(self, _settings):
        """
        Returns a list of filenames containing those GIMIAS plugin dlls which are not built by the current configuration (in _settings).
        """
        result = []
        instance = self.__GetProjectInstance(_settings)
        if not instance.name.lower() == "gimias":
            return result
    
        configuredPluginNames = [project.name.lower() for project in instance.GetProjects(_recursive = 1) ]
        for configuration in ("Debug", "Release"):
            pluginsFolder = "%s/bin/%s/plugins/*" % (_settings.buildFolder, configuration)

            for pluginFolder in glob.glob( pluginsFolder ):
                pluginName = os.path.basename(pluginFolder)
                if not os.path.isdir(pluginFolder) or pluginName.lower() in configuredPluginNames:
                    continue
                    
                searchPath = string.Template("$folder/lib/$config/$name.dll").substitute(folder = pluginFolder, config = configuration, name = pluginName )
                if os.path.exists( searchPath ):
                    result.append( searchPath )
                searchPath = string.Template("$folder/lib/$config/lib$name.so").substitute(folder = pluginFolder, config = configuration, name = pluginName )
                if os.path.exists( searchPath ):
                    result.append( searchPath )
                    
        return result

    def GetTargetSolutionPath(self, _settings):
        instance = self.__GetProjectInstance(_settings)
        return "%s/%s.sln" % (instance.GetBuildFolder(), instance.name)

    def GetThirdPartySolutionPath(self, _settings):
        return "%s/CILAB_TOOLKIT.sln" % (_settings.thirdPartyBinFolder)
    
    def UpdateRecentlyUsedCSnakeFiles(self, _settings):
        _settings.AddRecentlyUsed(_settings.instance, _settings.csnakeFile)

    def GetCategories(self, _settings):
        instance = self.__GetProjectInstance(_settings)
        categories = list()
        for project in instance.GetProjects(_recursive = True):
            for cat in project.categories:
                if not cat in categories:
                    categories.append(cat)
        return categories
                    