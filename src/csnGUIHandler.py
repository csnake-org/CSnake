import csnUtility
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
from csnListener import ChangeListener, ProgressEvent, ProgressListener
import logging

class RootNotFound(IOError):
    pass

class NotARoot(IOError):
    pass

class RollbackHandler:
    """
    This helper class instantiates the RollbackImporter and extends the python search path 
    """
    def SetUp(self, _projectPath, _rootFolders, _thirdPartyFolders):
        """
        Set up the roll back. 
        """
        # set up roll back of imported modules
        self.rbi = RollbackImporter.RollbackImporter()
        self.previousPaths = list(sys.path)
        
        # extend python path with project folder, source root and third party root
        newPaths = list(_rootFolders)
        newPaths.extend(_thirdPartyFolders) 
        newPaths.extend([_projectPath]) 
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
        self.contextFilename = None
        self.generator = csnGenerator.Generator()
        self.progressListener = ProgressListener(self)
        self.generator.AddListener(self.progressListener)
        # contains the last result of calling __GetProjectInstance
        self.cachedProjectInstance = None
        # logger
        self.__logger = logging.getLogger("CSnake")
        # change flags
        self.contextModified = False
        self.changeListener = ChangeListener(self)
        # listeners
        self.__listeners = []
        # progress start and range (in case of multiple actions)
        self.__progressStart = 0
        self.__progressRange = 100
        # error message
        self.__errorMessage = ""
    
    def LoadContext(self, filename):
        self.contextFilename = filename
        self.SetContext(csnContext.Load(filename))
        return self.context
        
    def SetContext(self, context):
        self.context = context
        self.context.AddListener(self.changeListener)
        csnProject.globalCurrentContext = self.context
   
    def __GetProjectInstance(self):
        """ Instantiates and returns the _instance in _projectPath. """
        self.DeletePycFiles()
        
        # set up roll back of imported modules
        rollbackHandler = RollbackHandler()
        rollbackHandler.SetUp(self.context.GetCsnakeFile(), self.context.GetRootFolders(), self.context.GetThirdPartyFolders())
        (projectFolder, name) = os.path.split(self.context.GetCsnakeFile())
        (name, _) = os.path.splitext(name)
        
        try:
            projectModule = csnUtility.LoadModule(projectFolder, name)
            projectModule # prevent warning
            exec "self.cachedProjectInstance = csnProject.ToProject(projectModule.%s)" % self.context.GetInstance()
        finally:
            # undo additions to the python path
            rollbackHandler.TearDown()

        relocator = csnPrebuilt.ProjectRelocator()
        relocator.Do(self.cachedProjectInstance, self.context.GetPrebuiltBinariesFolder())
        self.UpdateRecentlyUsedCSnakeFiles()
        
        return self.cachedProjectInstance
    
    def ConfigureProjectToBuildFolder(self, _alsoRunCMake):
        """ 
        Configures the project to the build folder.
        """
        instance = self.__GetProjectInstance()
        
        instance.installManager.ResolvePathsOfFilesToInstall()
        self.generator.Generate(instance)
        instance.dependenciesManager.WriteDependencyStructureToXML("%s/projectStructure.xml" % instance.GetBuildFolder())
        
        if _alsoRunCMake:
            # check if CMake is present
            self.CheckCMake()
        
            nProjects = len(instance.dependenciesManager.GetProjects(_recursive = True))
            argList = [self.context.GetCmakePath(), "-G", self.context.GetCompiler().GetName(), instance.GetCMakeListsFilename()]
            
            if self.__ConfigureProject(argList, instance.GetBuildFolder(), nProjects):
                self.generator.PostProcess(instance)
                return True
            else:
                return False
        
        return True
            
    def InstallBinariesToBuildFolder(self):
        return self.generator.InstallBinariesToBuildFolder(self.__GetProjectInstance())
             
    def CMakeIsFound(self):
        """ Check if Cmake is present by launching it. """
        found = os.path.exists(self.context.GetCmakePath()) and os.path.isfile(self.context.GetCmakePath())
        if not found:
            try:
                retcode = subprocess.Popen(self.context.GetCmakePath()).wait()
            except:
                retcode = 1
            found = retcode == 0
        return found        
    
    def CheckCMake(self):
        """ Check if Cmake is present. """
        if not os.path.exists( self.context.GetCmakePath() ):
            raise Exception( "Please provide a valid CMake path." )
    
    def ConfigureThirdPartyFolders(self, _nrOfTimes = 2):
        """ 
        Runs cmake to install the libraries in the third party folder.
        By default, the third party folder is configured twice because this works around
        some problems with incomplete configurations.
        """
        result = True
        nTP = self.context.GetNumberOfThirdPartyFolders()
        
        # set the progress range
        self.__progressRange = 100 / nTP
        # Configure third parties
        for index in range(0, nTP ):
            result = self.ConfigureThirdPartyFolder( self.context.GetThirdPartyFolder( index ), self.context.GetThirdPartyBuildFolderByIndex( index ), _nrOfTimes = _nrOfTimes, allBuildFolders = self.context.GetThirdPartyBuildFoldersComplete() )
            self.__progressStart += self.__progressRange
        # reset the progress range
        self.__progressStart = 0
        self.__progressRange = 100
        
        return result

    def ConfigureThirdPartyFolder(self, source, build, allBuildFolders, _nrOfTimes = 2):
        """ 
        Runs cmake to install the libraries in the third party folder.
        By default, the third party folder is configured twice because this works around
        some problems with incomplete configurations.
        """
        result = True
        
        # create the build folder if it doesn't exist
        os.path.exists(build) or os.makedirs(build)
        
        # check if CMake is present
        self.CheckCMake()
        
        cmakeModulePath = ""
        for buildFolder in allBuildFolders:
            cmakeModulePath = cmakeModulePath + buildFolder + ";"
        cmakeModulePath = cmakeModulePath[0:-1]
        argList = [self.context.GetCmakePath(), \
                  "-G", self.context.GetCompiler().GetName(), \
                  "-D", "THIRDPARTY_BUILD_FOLDERS:STRING='%s'" % cmakeModulePath] + \
                  self.context.GetCompiler().GetThirdPartyCMakeParameters() + \
                  [source]
        
        for _ in range(0, _nrOfTimes):
            result = result and self.__ConfigureThirdParty(argList, build) 

        return result

    def DeletePycFiles(self):
        """
        Tries to delete all pyc files from _projectPath, _rootFolders and thirdPartyFolders.
        However, __init__.pyc files are not removed.
        """
        # determine list of folders to search for pyc files
        folderList = []
        if self.context:
            folderList.extend(self.context.GetThirdPartyFolders())
            folderList.extend(self.context.GetRootFolders())

        # remove pyc files
        while len(folderList) > 0:
            newFolders = []
            for folder in folderList:
                pycFiles = [csnUtility.NormalizePath(x) for x in glob.glob("%s/*.pyc" % folder)]
                for pycFile in pycFiles:
                    if not os.path.basename(pycFile) == "__init__.pyc":
                        os.remove(pycFile)

                newFolders.extend( [csnUtility.NormalizePath(os.path.dirname(x)) for x in glob.glob("%s/*/__init__.py" % folder)] )
            folderList = list(newFolders)
        
    def GetListOfPossibleTargets(self):
        """
        Returns a list of possible targets which are defined in CSnake file _projectPath.
        """

        self.DeletePycFiles()
                
        rollbackHandler = RollbackHandler()
        rollbackHandler.SetUp(self.context.GetCsnakeFile(), self.context.GetRootFolders(), self.context.GetThirdPartyFolders())
        result = []

        # find csnake targets in the loaded module
        (projectFolder, name) = os.path.split(self.context.GetCsnakeFile())
        (name, _) = os.path.splitext(name)
        projectModule = csnUtility.LoadModule(projectFolder, name)   
        members = inspect.getmembers(projectModule)
        nMembers = len(members)
        count = 0
        for member in members:
            self.__NotifyListeners(ProgressEvent(self, count*100/nMembers))
            count += 1
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
            pluginsFolder = "%s/bin/%s/plugins/*" % (self.context.GetBuildFolder(), configuration)

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

    def IsContextModified(self):
        return self.contextModified
        
    def GetTargetSolutionPath(self):
        instance = self.cachedProjectInstance
        if not instance or self.IsContextModified():
            instance = self.__GetProjectInstance()
        path = ""
        if instance:
            path = "%s/%s.sln" % (instance.GetBuildFolder(), instance.name)
        return path

    def GetThirdPartySolutionPaths(self):
        result = []
        for folder in self.context.GetThirdPartyBuildFolders():
            result.append("%s/CILAB_TOOLKIT.sln" % (folder))
        return result

    def UpdateRecentlyUsedCSnakeFiles(self):
        self.context.AddRecentlyUsed(self.context.GetInstance(), self.context.GetCsnakeFile())

    def GetCategories(self, _forceRefresh = False):
        instance = self.cachedProjectInstance
        if _forceRefresh or self.IsContextModified() or instance == None:
            instance = self.__GetProjectInstance()
        categories = list()
        for project in instance.GetProjects(_recursive = True):
            for cat in project.categories:
                if not cat in categories:
                    categories.append(cat)
        return categories
                    
    def FindAdditionalRootFolders(self):
        ''' Look for folders with the rootFolder.csnake file. '''
        result = []
        folder = csnUtility.NormalizePath(os.path.dirname(self.context.GetCsnakeFile()))
        previousFolder = ""
        while folder != previousFolder:
            if os.path.exists("%s/rootFolder.csnake" % folder) and not folder in self.context.GetRootFolders():
                result.append(folder)
            previousFolder = folder
            folder = csnUtility.NormalizePath(os.path.split(folder)[0])
        return result

    def BuildMultiple(self, solutionNames, buildMode, isThirdParty):
        # result flag
        result = True
        # set the progress range
        self.__progressRange = 100 / len(solutionNames)
        # build the solutions
        for solutionName in solutionNames:
            result = result and self.Build(solutionName, buildMode, isThirdParty)
            self.__progressStart += self.__progressRange
        # reset the progress start and range
        self.__progressStart = 0
        self.__progressRange = 100
        
        return result

    def Build(self, solutionName, buildMode, isThirdParty):
        # result flag
        result = True

        # first progress
        progress = self.__progressStart
        self.__NotifyListeners(ProgressEvent(self,progress))

        # visual studio case
        if self.context.GetCompilername().startswith("Visual Studio"):
            # check solution exists
            if not os.path.exists(solutionName):
                raise Exception( "Solution file not found: %s" % solutionName )
            # set the path to the IDE
            pathIDE = self.context.GetIdePath()
            # for visual studio (not express), use the devenv.com
            (head, tail) = os.path.split(pathIDE)
            if tail == "devenv.exe":
                pathIDE = pathIDE.replace(".exe",".com")
            # exit if not found
            if not os.path.exists(pathIDE):
                raise Exception( "Please provide a valid Visual Studio path" )
            
            instance = self.__GetProjectInstance()
            nProjects = len(instance.dependenciesManager.GetProjects(_recursive = True))
            
            # build in debug
            self.__logger.info("Building '%s' in debug mode [visual studio]." % solutionName)
            result = result and self.__BuildVisualStudio(pathIDE, solutionName, "debug", nProjects)
            if not result: return False
            # build in release
            self.__logger.info("Building '%s' in release mode [visual studio]." % solutionName)
            result = result and self.__BuildVisualStudio(pathIDE, solutionName, "release", nProjects)
            if not result: return False
        
        elif self.context.GetCompilername().startswith("Unix") or \
             self.context.GetCompilername().startswith("KDevelop3") :
            # get the build path
            (head, tail) = os.path.split(solutionName)
            buildPath = head
            # special case for third parties
            if isThirdParty:
                buildPath = "%s/%s" % (buildPath, buildMode)
            # build
            self.__logger.info("Building '%s' [make]." % buildPath)
            result = result and self.__BuildMake(buildPath)
            
        # last progress
        self.__NotifyListeners(ProgressEvent(self,self.__progressRange))

        return result

    def SetContextModified(self, modified):
        self.contextModified = modified

    def StateChanged(self, event):
        """ Called by the ChangeListener. """
        if event.IsChange():
            self.SetContextModified(True)
            
    def ProgressChanged(self, event):
        """ Called by the ProgressListener. """
        if event.IsProgress():
            # propagate...
            self.__NotifyListeners(event)

    def __NotifyListeners(self, event):
        """ Notify the attached listeners about the event. """
        for listener in self.__listeners:
            listener.Update(event)
        
    def AddListener(self, listener):
        """ Attach a listener to this class. """
        if not listener in self.__listeners:
            self.__listeners.append(listener)
    
    def __SetErrorMessage(self, message):
        self.__errorMessage = message
        
    def GetErrorMessage(self):
        return self.__errorMessage
    
    def __ConfigureThirdParty(self, argList, workingDir):
        """ Run cmake on a third party. Returns True is success. """
        # reset errors
        self.__SetErrorMessage("")
        # run process
        sub = subprocess.Popen(argList, cwd=workingDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # catch lines to indicate progress (has to be bellow Popen)
        while True:
            line = sub.stdout.readline()
            if not line: 
                break
            sys.stdout.write(line)
        # wait till the process finishes
        res = (sub.wait() == 0)
        # catch error lines
        message = ""
        for line in sub.stderr.readlines():
            message += line.rstrip('\n')
        sys.stderr.write(message)
        self.__SetErrorMessage(message)
        # return result
        return res
    
    def __ConfigureProject(self, argList, workingDir, nProjects):
        """ Run cmake on a project. Returns True is success. """
        # reset errors
        self.__SetErrorMessage("")
        # run process
        sub = subprocess.Popen(argList, cwd=workingDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # catch lines to indicate progress (has to be bellow Popen)
        count = 0
        while True:
            line = sub.stdout.readline()
            if not line:
                break
            sys.stdout.write(line)
            # progress: looks like '-- Processing ...'
            str = line[0:13].strip()
            if str == "-- Processing":
                progress = count*100/nProjects
                if progress > 100: progress = 100
                self.__NotifyListeners(ProgressEvent(self,progress))
                count += 1
        # wait till the process finishes
        res = (sub.wait() == 0)
        # catch error lines
        message = ""
        for line in sub.stderr.readlines():
            message += line.rstrip('\n')
        sys.stderr.write(message)
        self.__SetErrorMessage(message)
        # return result
        return res
    
    def __BuildVisualStudio(self, pathIDE, solution, buildMode, nProjects):
        """ Build using the Visual Studio Compiler. Returns True is success. """
        # reset errors
        self.__SetErrorMessage("")
        # arguments
        argList = [pathIDE, solution, "/build", buildMode ]
        # run process
        sub = subprocess.Popen(argList, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # catch lines to indicate progress (has to be bellow Popen)
        count = 0
        while True:
            line = sub.stdout.readline()
            if not line:
                break
            sys.stdout.write(line)
            # progress: looks like '#>Build log was saved'
            str = line[1:11].strip()
            if str == ">Build log":
                progress = count*100/nProjects
                if progress > 100: progress = 100
                self.__NotifyListeners(ProgressEvent(self,progress))
                count += 1
        # wait till the process finishes
        res = (sub.wait() == 0)
        # catch error lines
        message = ""
        for line in sub.stderr.readlines():
            message += line.rstrip('\n')
        sys.stderr.write(message)
        self.__SetErrorMessage(message)
        # return result
        return res
    
    def __BuildMake(self, buildPath):
        """ Build using Make. Returns True is success. """
        # reset errors
        self.__SetErrorMessage("")
        # arguments
        argList = ["make", "-s"]
        # run process
        sub = subprocess.Popen(argList, cwd=buildPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # catch lines to indicate progress (has to be bellow Popen)
        while True:
            line = sub.stdout.readline()
            if not line: 
                break
            sys.stdout.write(line)
            # progress: looks like '[ 10%] ...'
            str = line[1:4].strip()
            if str.isdigit():
                progress = self.__progressStart + int(str)*self.__progressRange/100
                if progress > 100: progress = 100
                self.__NotifyListeners(ProgressEvent(self, progress))
        # wait till the process finishes
        res = (sub.wait() == 0)
        # catch error lines
        message = ""
        for line in sub.stderr.readlines():
            message += line.rstrip('\n')
        sys.stderr.write(message)
        self.__SetErrorMessage(message)
        # return result
        return res
