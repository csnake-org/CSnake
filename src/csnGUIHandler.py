## @package csnGUIHandler
# Definition of GUI handling classes. 
import csnAPIPublic # not used here, but necessary in order to keep the function GetAPI working after the rollback handler has been executed (e.g. in callback functions registered via AddPostCMakeTasks)
import csnUtility
import csnContext
import csnGenerator
import csnProject
import csnPrebuilt
import csnAPIImplementation
import RollbackImporter
import glob
import json
import inspect
import string
import os
import subprocess
import sys
from csnListener import ChangeListener, ProgressEvent, ProgressListener
import logging
import copy

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
        self.generator = csnGenerator.Generator()
        self.progressListener = ProgressListener(self)
        self.generator.AddListener(self.progressListener)
        # contains the last result of calling __GetProjectInstance
        self.cachedProjectModule = None
        self.cachedProjectInstance = dict()
        self.cachedProjectInstanceContext = None
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
        self.__userCanceled = False
        # error message
        self.__errorMessage = ""
        self.__errorFilename = "%s/errors.txt" % csnUtility.GetCSnakeUserFolder() 
    
    def LoadContext(self, filename):
        self.SetContext(csnContext.Load(filename))
        return self.context
        
    def SetContext(self, context):
        self.context = context
        self.context.AddListener(self.changeListener)
        csnProject.globalCurrentContext = self.context
        
    def Cancel(self):
        self.__userCanceled = True
        if self.__GetProjectInstance():
            self.__GetProjectInstance().installManager.Cancel()
        
    def __ResetCancel(self):
        self.__userCanceled = False
        
    def IsCanceled(self):
        return self.__userCanceled
    
    def __CheckReloadChanges(self, contextA, contextB):
        """Have there been done changes to the context that justify reloading the .py files?"""
        # changes that justify reload: src, TP-src, Compiler, Compile-Mode, csn-file
        functionsToCompare = [csnContext.ContextData.GetRootFolders,
                                csnContext.ContextData.GetBuildFolder,
                                csnContext.ContextData.GetThirdPartySrcFolders,
                                csnContext.ContextData.GetThirdPartyBuildFolders,
                                csnContext.ContextData.GetCompilername,
                                csnContext.ContextData.GetConfigurationName,
                                csnContext.ContextData.GetCsnakeFile]
        
        if contextA is None or contextB is None:
            return True
        for function in functionsToCompare:
            if function(contextA) != function(contextB):
                return True
        return False
    
    def __GetProjectModule(self, _forceReload = True):
        reloadFiles = _forceReload or self.__CheckReloadChanges(self.cachedProjectInstanceContext, self.context.GetData())
        
        if reloadFiles or self.cachedProjectModule is None:
            # reset cached stuff
            self.cachedProjectInstanceContext = copy.deepcopy(self.context.GetData())
            self.cachedProjectInstance = dict()
            self.DeletePycFiles()
            
            # set up roll back of imported modules
            rollbackHandler = RollbackHandler()
            rollbackHandler.SetUp(self.context.GetCsnakeFile(), self.context.GetRootFolders(), self.context.GetThirdPartyFolders())
            (projectFolder, name) = os.path.split(self.context.GetCsnakeFile())
            (name, _) = os.path.splitext(name)
            
            try:
                self.cachedProjectModule = csnUtility.LoadModule(projectFolder, name)
            finally:
                # undo additions to the python path
                rollbackHandler.TearDown()
            
            self.UpdateRecentlyUsedCSnakeFiles()
        return self.cachedProjectModule
    
    def __GetProjectInstance(self, _forceReload = False):
        """ Instantiates and returns the _instance in _projectPath. """
        instanceName = self.context.GetInstance()
        reloadFiles = _forceReload or self.__CheckReloadChanges(self.cachedProjectInstanceContext, self.context.GetData())
        
        if not instanceName in self.cachedProjectInstance or reloadFiles:
            projectModule = self.__GetProjectModule(_forceReload = _forceReload)
            exec "self.cachedProjectInstance[instanceName] = csnProject.ToProject(projectModule.%s)" % instanceName
            if isinstance(self.cachedProjectInstance[instanceName], csnAPIImplementation._APIGenericProject_Base):
                # Unwrap it from the API
                self.cachedProjectInstance[instanceName]=self.cachedProjectInstance[instanceName]._APIGenericProject_Base__project
            elif not isinstance(self.cachedProjectInstance[instanceName], csnProject.GenericProject):
                # Neither wrapped nor unwrapped project?
                raise Exception("Instance \"%s\" is not a valid CSnake project, but rather of type \"%s\"!" %
                        (instanceName, type(self.cachedProjectInstance[instanceName]).__name__))
            relocator = csnPrebuilt.ProjectRelocator()
            relocator.Do(self.cachedProjectInstance[instanceName], self.context.GetPrebuiltBinariesFolder())
            self.UpdateRecentlyUsedCSnakeFiles()
        
        return self.cachedProjectInstance[instanceName]

    def WriteDumpFileAndProjectStructureToBuildFolder(self, instance):
        """
        Writes a json file with all gathered information for instance to the build folder
        """
        dumpFilename = "%s/projectData.json" % instance.GetBuildFolder()
        dumpFile = open(dumpFilename, 'w')
        dumpFile.write(json.dumps(instance.Dump(), sort_keys=True, indent=2))
        dumpFile.close()
        instance.dependenciesManager.WriteDependencyStructureToXML("%s/projectStructure.xml" % instance.GetBuildFolder())

    def ConfigureProjectToBuildFolder(self, _alsoRunCMake, _askUser = None):
        """ 
        Configures the project to the build folder.
        """
        instance = self.__GetProjectInstance()
        
        instance.installManager.ResolvePathsOfFilesToInstall()
        self.generator.Generate(instance)
        self.WriteDumpFileAndProjectStructureToBuildFolder(instance)

        if _alsoRunCMake:
            # check if CMake is present
            self.CheckCMake()
        
            nProjects = len(instance.dependenciesManager.GetProjects(_recursive = True, _includeSelf = True))
            #argList = [self.context.GetCmakePath(), "-G", self.context.GetCompiler().GetName(), instance.GetCMakeListsFilename()]
            argList = [self.context.GetCmakePath(), \
                  "-G", self.context.GetCompiler().GetName()] + \
                  self.context.GetCompiler().GetProjectCMakeParameters() + \
                  [instance.GetCMakeListsFilename()]

            if self.__ConfigureProject(argList, instance.GetBuildFolder(), nProjects):
                self.generator.PostProcess(instance)
            else:
                return False
        
        for project in instance.dependenciesManager.GetProjects(_recursive = True) + [instance]:
            if isinstance(project, csnProject.GenericProject):
                for task in project.GetPostCMakeTasks():
                    task(project, _askUser)
        
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
    
    def ConfigureThirdPartyFolders(self):
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
            result = self.ConfigureThirdPartyFolder( self.context.GetThirdPartyFolder( index ), self.context.GetThirdPartyBuildFolderByIndex( index ), allBuildFolders = self.context.GetThirdPartyBuildFoldersComplete() )
            self.__progressStart += self.__progressRange
        # reset the progress range
        self.__progressStart = 0
        self.__progressRange = 100
        
        return result

    def ConfigureThirdPartyFolder(self, source, build, allBuildFolders):
        """ 
        Runs cmake to install the libraries in the third party folder.
        @param source: The source folder.
        @param build: The build folder.
        @param allBuildFolders: Root of the build folder.
        """
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
        
        return self.__ConfigureThirdParty(argList, build) 

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
        self.__ResetCancel()
                
        # load module - technically _forceReload is not necessary here, it is just set to maintain the current user experience (the
        # user expect a reload when he clicks on the "update" button - we should give him an extra button to do so in the future)
        projectModule = self.__GetProjectModule(_forceReload = True)
        # find csnake targets in the loaded module
        members = inspect.getmembers(projectModule)
        nMembers = len(members)
        count = 0
        result = []
        for member in members:
            self.__NotifyListeners(ProgressEvent(self, count*100/nMembers))
            if self.IsCanceled(): return result
            count += 1
            (targetName, target) = (member[0], member[1])
            if isinstance(target, csnProject.VeryGenericProject):
                result.append(targetName)
            elif isinstance(target, csnAPIImplementation._APIVeryGenericProject_Base):
                result.append(targetName)
        
        return result
        
    def IsContextModified(self):
        return self.contextModified
        
    def GetTargetSolutionPath(self):
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
        instance = self.__GetProjectInstance(_forceRefresh)
        categories = dict()
        for project in instance.GetProjects(_recursive=True, _filter=False, _onlyRequiredProjects=False, _includeSelf=True):
            for cat in project.categories:
                if not cat in categories:
                    categories[cat] = project
        return categories
    
    def GetProjectDependencies(self):
        return self.__GetProjectInstance().GetProjects(_recursive=True, _onlyRequiredProjects=True)
    
    def GetInstanceCategories(self):
        return self.__GetProjectInstance().categories
                    
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
        # log
        self.__logger.info("Running cmake in: %s" % workingDir)
        # reset errors
        self.__ResetCancel()
        self.__SetErrorMessage("")
        # run process
        errorFile = open(self.__errorFilename, 'w')
        sub = subprocess.Popen(argList, cwd=workingDir, stdout=subprocess.PIPE, stderr=errorFile)
        # catch lines to indicate progress (has to be bellow Popen)
        count = 0
        tpFolder = argList[len(argList)-1]
        dirs = [d for d in os.listdir(tpFolder) if os.path.isdir(os.path.join(tpFolder, d))]
        nProjects = len(dirs)
        while True:
            line = sub.stdout.readline()
            if not line: 
                break
            sys.stdout.write(line)
            # progress: looks like '-- Processing ...'
            str = line[0:11].strip()
            if str == "-- Parsing":
                progress = count*100/nProjects
                if progress >= 100: progress = 99
                self.__NotifyListeners(ProgressEvent(self,progress))
                if self.IsCanceled(): return False
                count += 1
        # wait till the process finishes
        res = (sub.wait() == 0)
        errorFile.close()
        # process error file
        if( os.path.getsize(self.__errorFilename) != 0 ):
            self.__ProcessErrorFile()
        # return result
        return res
    
    def __ConfigureProject(self, argList, workingDir, nProjects):
        """ Run cmake on a project. Returns True is success. """
        # log
        self.__logger.info("Running cmake in: %s" % workingDir)
        # reset errors
        self.__ResetCancel()
        self.__SetErrorMessage("")
        # run process
        errorFile = open(self.__errorFilename, 'w')
        sub = subprocess.Popen(argList, cwd=workingDir, stdout=subprocess.PIPE, stderr=errorFile)
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
                if progress >= 100: progress = 99
                self.__NotifyListeners(ProgressEvent(self,progress))
                if self.IsCanceled(): return False
                count += 1
        # wait till the process finishes
        res = (sub.wait() == 0)
        errorFile.close()
        # process error file
        if( os.path.getsize(self.__errorFilename) != 0 ):
            self.__ProcessErrorFile()
        # return result
        return res
    
    def __BuildVisualStudio(self, pathIDE, solution, buildMode, nProjects):
        """ Build using the Visual Studio Compiler. Returns True is success. """
        # log
        self.__logger.info("Running vc for: %s" % solution)
        # reset errors
        self.__ResetCancel()
        self.__SetErrorMessage("")
        # arguments
        argList = [pathIDE, solution, "/build", buildMode ]
        # run process
        errorFile = open(self.__errorFilename, 'w')
        sub = subprocess.Popen(argList, stdout=subprocess.PIPE, stderr=errorFile)
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
                if progress >= 100: progress = 99
                self.__NotifyListeners(ProgressEvent(self,progress))
                if self.IsCanceled(): return False
                count += 1
        # wait till the process finishes
        res = (sub.wait() == 0)
        errorFile.close()
        # process error file
        if( os.path.getsize(self.__errorFilename) != 0 ):
            self.__ProcessErrorFile()
        # return result
        return res
    
    def __BuildMake(self, buildPath):
        """ Build using Make. Returns True is success. """
        # log
        self.__logger.info("Running make in: %s" % buildPath)
        # reset errors
        self.__ResetCancel()
        self.__SetErrorMessage("")
        # arguments
        argList = ["make", "-s"]
        # run process
        errorFile = open(self.__errorFilename, 'w')
        sub = subprocess.Popen(argList, cwd=buildPath, stdout=subprocess.PIPE, stderr=errorFile)
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
                if progress >= 100: progress = 99
                self.__NotifyListeners(ProgressEvent(self, progress))
                if self.IsCanceled(): return False
        # wait till the process finishes
        res = (sub.wait() == 0)
        errorFile.close()
        # process error file
        if( os.path.getsize(self.__errorFilename) != 0 ):
            self.__ProcessErrorFile()
        # return result
        return res
    
    def __ProcessErrorFile(self):
        """ Process an error stream. """
        limit = 10
        # error lines
        errorFile = open(self.__errorFilename, 'r')
        errorLines = errorFile.readlines()
        nLines = len(errorLines)
        # output all to console
        for line in errorLines:
            sys.stderr.write(line)
        # error message, limit if too big
        iMax = nLines
        if nLines >= limit:
            iMax = limit
        message = ""
        for i in range(0,iMax):
            message += errorLines[i]
        # if too long, tell the user
        if nLines >= limit:
            message += "\n... and more ..."
            message += "\nSee error log (%s) for full details." % self.__errorFilename
        # save message    
        self.__SetErrorMessage(message)
        # close
        errorFile.close()
