import csnUtility
import csnBuild
import csnContext
import csnGenerator
import csnProject
import csnPrebuilt
import RollbackImporter
import glob
import inspect
import string
import os
import subprocess
import sys

class RootNotFound(IOError):
    pass

class NotARoot(IOError):
    pass

class TypeError(StandardError):
    pass

class RollbackHandler:
    """
    This helper class instantiates the RollbackImporter and extends the python search path 
    """
    def SetUp(self, _projectPath, _rootFolders, _thirdPartyRootFolder):
        """
        Set up the roll back. 
        """
        # set up roll back of imported modules
        self.rbi = RollbackImporter.RollbackImporter()
        self.previousPaths = list(sys.path)
        
        # extend python path with project folder, source root and third party root
        newPaths = list(_rootFolders)
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
        self.context = None
        self.generator = csnGenerator.Generator()
        # contains the last result of calling __GetProjectInstance
        self.cachedProjectInstance = None
    
    def LoadContext(self, filename):
        self.contextFilename = filename
        self.context = csnContext.Load(filename)
        csnProject.globalCurrentContext = self.context
        return self.context
        
    def __GetProjectInstance(self):
        """ Instantiates and returns the _instance in _projectPath. """
        self.DeletePycFiles()
        
        # set up roll back of imported modules
        rollbackHandler = RollbackHandler()
        rollbackHandler.SetUp(self.context.csnakeFile, self.context.rootFolders, self.context.thirdPartyRootFolder)
        (projectFolder, name) = os.path.split(self.context.csnakeFile)
        (name, _) = os.path.splitext(name)
        
        try:
            projectModule = csnUtility.LoadModule(projectFolder, name)
            projectModule # prevent warning
            exec "self.cachedProjectInstance = csnProject.ToProject(projectModule.%s)" % self.context.instance
        finally:
            # undo additions to the python path
            rollbackHandler.TearDown()

        relocator = csnPrebuilt.ProjectRelocator()
        relocator.Do(self.cachedProjectInstance, self.context.prebuiltBinariesFolder)
        self.UpdateRecentlyUsedCSnakeFiles()
        
        return self.cachedProjectInstance
    
    def ConfigureProjectToBinFolder(self, _alsoRunCMake, _callback = None):
        """ 
        Configures the project to the bin folder.
        """
        instance = self.__GetProjectInstance()
        instance.installManager.ResolvePathsOfFilesToInstall(self.context.thirdPartyBinFolder)
        self.generator.Generate(instance)
        instance.dependenciesManager.WriteDependencyStructureToXML("%s/projectStructure.xml" % instance.GetBuildFolder())
            
        if _alsoRunCMake:
            argList = [self.context.cmakePath, "-G", self.context.compiler, instance.GetCMakeListsFilename()]
            process = subprocess.Popen(argList, cwd = instance.GetBuildFolder()) # , stdout=subProcess.PIPE, stderr=subProcess.PIPE
            while process.poll() is None:
                (outdata, errdata) = process.communicate()
                if _callback:
                    _callback.Report(outdata)
                    _callback.Error(errdata)
            if process.poll() == 0:
                self.generator.PostProcess(instance)
                return True
            else:
                _callback.Warn("Configuration failed.")
                if not self.CMakeIsFound():
                    _callback.Warn("CMake not found at %s" % self.context.cmakePath)
                return False
            
    def InstallBinariesToBinFolder(self):
        return self.generator.InstallBinariesToBinFolder(self.__GetProjectInstance())
             
    def CMakeIsFound(self):
        found = os.path.exists(self.context.cmakePath) and os.path.isfile(self.context.cmakePath)
        if not found:
            try:
                retcode = subprocess.Popen(self.context.cmakePath).wait()
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
        os.path.exists(self.context.thirdPartyBinFolder) or os.makedirs(self.context.thirdPartyBinFolder)
        argList = [self.context.cmakePath, "-G", self.context.compiler, self.context.thirdPartyRootFolder]
        for _ in range(0, _nrOfTimes):
            result = result and 0 == subprocess.Popen(argList, cwd = self.context.thirdPartyBinFolder).wait() 

        if not result:
            print "Configuration failed.\n"   
            if not self.CMakeIsFound():
                print "Please specify correct path to CMake (current is %s)" % self.context.cmakePath 
                return False
            
        return result

    def DeletePycFiles(self):
        """
        Tries to delete all pyc files from _projectPath, _rootFolders and thirdPartyRootFolder.
        However, __init__.pyc files are not removed.
        """
        # determine list of folders to search for pyc files
        folderList = [self.context.thirdPartyRootFolder]
        folderList.extend(self.context.rootFolders)
                    
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
        rollbackHandler.SetUp(self.context.csnakeFile, self.context.rootFolders, self.context.thirdPartyRootFolder)
        result = []

        # find csnake targets in the loaded module
        (projectFolder, name) = os.path.split(self.context.csnakeFile)
        (name, _) = os.path.splitext(name)
        projectModule = csnUtility.LoadModule(projectFolder, name)   
        for member in inspect.getmembers(projectModule):
            (targetName, target) = (member[0], member[1])
            if isinstance(target, csnProject.GenericProject):
                result.append(targetName)
        
        rollbackHandler.TearDown()
        return result
        
    def GetListOfSpuriousPluginDlls(self, _reuseInstance = False):
        """
        Returns a list of filenames containing those GIMIAS plugin dlls which are not built by the current configuration.
        """
        result = []
        instance = self.cachedProjectInstance
        if not _reuseInstance:
            instance = self.__GetProjectInstance()
        if not instance.name.lower() == "gimias":
            return result
    
        configuredPluginNames = [project.name.lower() for project in instance.GetProjects(_recursive = 1) ]
        for configuration in ("Debug", "Release"):
            pluginsFolder = "%s/bin/%s/plugins/*" % (self.context.buildFolder, configuration)

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

    def GetTargetSolutionPath(self, _reuseInstance = False):
        instance = self.cachedProjectInstance
        if not _reuseInstance:
            instance = self.__GetProjectInstance()
        return "%s/%s.sln" % (instance.GetBuildFolder(), instance.name)

    def GetThirdPartySolutionPath(self):
        return "%s/CILAB_TOOLKIT.sln" % (self.context.thirdPartyBinFolder)
    
    def UpdateRecentlyUsedCSnakeFiles(self):
        self.context.AddRecentlyUsed(self.context.instance, self.context.csnakeFile)

    def GetCategories(self):
        instance = self.__GetProjectInstance()
        categories = list()
        for project in instance.GetProjects(_recursive = True):
            for cat in project.categories:
                if not cat in categories:
                    categories.append(cat)
        return categories
                    