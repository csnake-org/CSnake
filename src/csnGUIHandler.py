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
    def __init__(self, _settings):
        """ 
        _settings - Instance of csnGenerator.Settings
        """
        self.options = 0
        self.settings = _settings
        pass
    
    def SetOptions(self, _options):
        # Set options described by csnGUIOptions.Options
        self.options = _options
        self.SetPythonPath(_options.pythonPath)
        return True
        
    def SetPythonPath(self, path):
        csnBuild.globalSettings.pythonPath = path
        if not (os.path.exists(csnBuild.globalSettings.pythonPath) and os.path.isfile(csnBuild.globalSettings.pythonPath)):
            print "Warning: python not found at: %s. Check the path in the Options menu.\n" % csnBuild.globalSettings.pythonPath
        
        return 1
        
    def __GetProjectInstance(self):
        """ Instantiates and returns the _instance in _projectPath. """
        csnBuild.globalSettings.filter = self.settings.filter
        csnBuild.globalSettings.testRunnerTemplate = self.settings.testRunnerTemplate
        self.DeletePycFiles()
        
        # set up roll back of imported modules
        rollbackHandler = RollbackHandler()
        rollbackHandler.SetUp(self.settings.csnakeFile, self.settings.rootFolders, self.settings.thirdPartyRootFolder)
        
        csnCilab.thirdPartyModuleFolder = self.settings.thirdPartyRootFolder
        csnCilab.thirdPartyBinFolder = self.settings.thirdPartyBinFolder
        
        (projectFolder, name) = os.path.split(self.settings.csnakeFile)
        (name, ext) = os.path.splitext(name)
        
        try:
            if self.settings.compiler in ("KDevelop3", "Unix Makefiles"):
                csnBuild.globalSettings.compilerType = csnKDevelop.Compiler
            elif self.settings.compiler == "Visual Studio 7 .NET 2003":
                csnBuild.globalSettings.compilerType = csnVisualStudio2003.Compiler
            elif self.settings.compiler in ("Visual Studio 8 2005", "Visual Studio 8 2005 Win64"):
                csnBuild.globalSettings.compilerType = csnVisualStudio2005.Compiler
            else:
                assert false, "\n\nError: Unknown compiler %s\n" % self.settings.compiler
                
            project = csnUtility.LoadModule(projectFolder, name)
            exec "instance = csnBuild.ToProject(project.%s)" % self.settings.instance
        finally:
            # undo additions to the python path
            rollbackHandler.TearDown()

        instance.compiler.SetBuildFolder(self.settings.buildFolder)
        relocator = csnPrebuilt.ProjectRelocator()
        relocator.Do(instance, self.settings.prebuiltBinariesFolder)
        
        self.UpdateRecentlyUsedCSnakeFiles()
        return instance
    
    def ConfigureProjectToBinFolder(self, _alsoRunCMake):
        """ 
        Configures the project to the bin folder.
        """
        logString = ""
        instance = self.__GetProjectInstance()

        generator = csnBuild.Generator(self.settings)
        instance.ResolvePathsOfFilesToInstall(self.settings.thirdPartyBinFolder)
        
        generator.Generate(instance)
        instance.WriteDependencyStructureToXML("%s/projectStructure.xml" % instance.GetBuildFolder())
            
        if _alsoRunCMake:
            argList = [self.settings.cmakePath, "-G", self.settings.compiler, instance.GetCMakeListsFilename()]
            retcode = subprocess.Popen(argList, cwd = self.settings.buildFolder).wait()
            if retcode == 0:
                generator.PostProcess(instance)
                return True
            else:
                print "Configuration failed.\n"   
                if not self.CMakeIsFound():
                    print "CMake not found at %s" % self.settings.cmakePath 
                return False
            
    def InstallBinariesToBinFolder(self):
        """ 
        This function copies all third party dlls to the binary folder, so that you can run the executables in the
        binary folder without having to build the INSTALL target.
        """
        result = True
        instance = self.__GetProjectInstance()
        instance.ResolvePathsOfFilesToInstall(self.settings.thirdPartyBinFolder)
        
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
        found = os.path.exists(self.settings.cmakePath) and os.path.isfile(self.settings.cmakePath)
        if not found:
            try:
                retcode = subprocess.Popen(self.cmakePath).wait()
            except:
                retcode = 1
            found = retcode == 0
        return found        
    
    def ConfigureThirdPartyFolder(self, _nrOfTimes = 2):
        """ 
        Runs cmake to install the libraries in the third party folder.
        By default, the third party folder is configured twice because this works around
        some problems with incomplete configurations.
        """
        result = True
        os.path.exists(self.settings.thirdPartyBinFolder) or os.makedirs(self.settings.thirdPartyBinFolder)
        argList = [self.settings.cmakePath, "-G", self.settings.compiler, self.settings.thirdPartyRootFolder]
        for i in range(0, _nrOfTimes):
            i # prevent warning
            result = result and 0 == subprocess.Popen(argList, cwd = self.settings.thirdPartyBinFolder).wait() 

        if not result:
            print "Configuration failed.\n"   
            if not self.CMakeIsFound():
                print "Please specify correct path to CMake (current is %s)" % self.settings.cmakePath 
                return False
            
        return result

    def DeletePycFiles(self):
        """
        Tries to delete all pyc files from _projectPath, _sourceRootFolders and thirdPartyRootFolder.
        However, __init__.pyc files are not removed.
        """
        # determine list of folders to search for pyc files
        folderList = [self.settings.thirdPartyRootFolder]
        folderList.extend(self.settings.rootFolders)
                    
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
        
    def GetListOfPossibleTargets(self):
        """
        Returns a list of possible targets which are defined in CSnake file _projectPath.
        """

        self.DeletePycFiles()
                
        rollbackHandler = RollbackHandler()
        rollbackHandler.SetUp(self.settings.csnakeFile, self.settings.rootFolders, self.settings.thirdPartyRootFolder)
        result = []

        # find csnake targets in the loaded module
        (projectFolder, name) = os.path.split(self.settings.csnakeFile)
        (name, ext) = os.path.splitext(name)
        csnCilab.thirdPartyModuleFolder = self.settings.thirdPartyRootFolder
        project = csnUtility.LoadModule(projectFolder, name)   
        for member in inspect.getmembers(project):
            if isinstance(member[1], csnBuild.Project):
                result.append(member[0])
        
        rollbackHandler.TearDown()
        return result
        
    def GetListOfSpuriousPluginDlls(self):
        """
        Returns a list of filenames containing those GIMIAS plugin dlls which are not built by the current configuration.
        """
        result = []
        instance = self.__GetProjectInstance()
        if not instance.name.lower() == "gimias":
            return result
    
        configuredPluginNames = [project.name.lower() for project in instance.GetProjects(_recursive = 1) ]
        for configuration in ("Debug", "Release"):
            pluginsFolder = "%s/bin/%s/plugins/*" % (self.settings.buildFolder, configuration)

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

    def GetTargetSolutionPath(self):
        instance = self.__GetProjectInstance()
        return "%s/%s.sln" % (instance.GetBuildFolder(), instance.name)

    def GetThirdPartySolutionPath(self):
        return "%s/CILAB_TOOLKIT.sln" % (self.settings.thirdPartyBinFolder)
    
    def UpdateRecentlyUsedCSnakeFiles(self):
        self.settings.AddRecentlyUsed(self.settings.instance, self.settings.csnakeFile)

    def GetCategories(self):
        instance = self.__GetProjectInstance()
        categories = list()
        for project in instance.GetProjects(_recursive = True):
            for cat in project.categories:
                if not cat in categories:
                    categories.append(cat)
        return categories
                    