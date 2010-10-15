import csnUtility
import os
import glob
import shutil
import GlobDirectoryWalker
import logging
from csnListener import ProgressEvent

class Manager:
    def __init__(self, _project):
        self.project = _project
        self.filesToInstall = dict()
        self.filesToInstall["Debug"] = dict()
        self.filesToInstall["Release"] = dict()
        # listeners
        self.__listeners = []
        # logger
        self.__logger = logging.getLogger("CSnake")
        # cancel flag
        self.__userCanceled = False

    def Cancel(self):
        self.__userCanceled = True
        
    def __ResetCancel(self):
        self.__userCanceled = False
        
    def IsCanceled(self):
        return self.__userCanceled
   
    def AddFilesToInstall(self, _list, _location = None, _debugOnly = 0, _releaseOnly = 0, _WIN32 = 0, _NOT_WIN32 = 0):
        if not self.project.context.GetCompiler().IsForPlatform(_WIN32, _NOT_WIN32):
            return
            
        if _location is None:
            _location = '.'
            
        for file in _list:
            if not _debugOnly:
                if not self.filesToInstall["Release"].has_key(_location):
                    self.filesToInstall["Release"][_location] = []
                if not file in self.filesToInstall["Release"][_location]:
                    self.filesToInstall["Release"][_location].append( file )
            if not _releaseOnly:
                if not self.filesToInstall["Debug"].has_key(_location):
                    self.filesToInstall["Debug"][_location] = []
                if not file in self.filesToInstall["Debug"][_location]:
                    self.filesToInstall["Debug"][_location].append( file )
    
    def ResolvePathsOfFilesToInstall(self, _skipCVS = 1):
        """ 
        This function replaces relative paths and wildcards in self.filesToInstall with absolute paths without wildcards.
        Any folder is replaced by a complete list of the files in that folder.
        _skipCVS - If true, folders called CVS and .svn are automatically skipped. 
        """
        excludedFolderList = ("CVS", ".svn")
        for mode in ("Debug", "Release"):
            for project in self.project.GetProjects(_recursive = 1, _includeSelf = True):
                filesToInstall = dict()
                for location in project.installManager.filesToInstall[mode].keys():
                    for dllPattern in project.installManager.filesToInstall[mode][location]:
                        for tpfolder in self.project.context.GetThirdPartyBuildFolders():
                            tpfolder += "/" + self.project.context.GetCompiler().GetThirdPartySubFolder()
                            path = csnUtility.NormalizePath(dllPattern)
                            if not os.path.isabs(path):
                                path = "%s/%s" % (tpfolder, path)
                            for file in glob.glob(path):
                                if (os.path.basename(file) in excludedFolderList) and _skipCVS and os.path.isdir(file):
                                    continue
                                if os.path.isdir(file):
                                    for folderFile in GlobDirectoryWalker.Walker(file, ["*"], excludedFolderList):
                                        if not os.path.isdir(folderFile):
                                            normalizedLocation = location + "/" + csnUtility.RemovePrefixFromPath(os.path.dirname(folderFile), file)
                                            normalizedLocation = csnUtility.NormalizePath(normalizedLocation)
                                            if not filesToInstall.has_key(normalizedLocation):
                                                filesToInstall[normalizedLocation] = []
                                            filesToInstall[normalizedLocation].append(csnUtility.NormalizePath(folderFile))
                                else:
                                    normalizedLocation = csnUtility.NormalizePath(location)
                                    if not filesToInstall.has_key(normalizedLocation):
                                        filesToInstall[normalizedLocation] = []
                                    filesToInstall[normalizedLocation].append(csnUtility.NormalizePath(file))
                    
                project.installManager.filesToInstall[mode] = filesToInstall
 
    def InstallBinariesToBuildFolder(self):
        """ 
        This function copies all third party dlls to the build folder, so that you can run the executables in the
        build folder without having to build the INSTALL target.
        """
        self.__ResetCancel()
        result = True
        self.ResolvePathsOfFilesToInstall()

        logger = logging.getLogger("CSnake")
        logger.info( "Install Binaries To Build Folder." )
        
        # progress
        progress = 0
        # increment = 100 / (n1 modes * n2 projects * n3 locations * n4 files)
        # n are taken from the first valid array values
        increment = 100.0
        
        for mode in ("Debug", "Release"):
            n1 = 2
            outputFolder = self.project.context.GetOutputFolder(mode)
            os.path.exists(outputFolder) or os.makedirs(outputFolder)
            for project in self.project.GetProjects(_recursive = 1, _includeSelf = True):
                n2 = len(self.project.GetProjects(_recursive = 1, _includeSelf = True))
                for location in project.installManager.filesToInstall[mode].keys():
                    n3 = len(project.installManager.filesToInstall[mode].keys())
                    for file in project.installManager.filesToInstall[mode][location]:
                        n4 = len(project.installManager.filesToInstall[mode][location])
                        if increment == 100:
                            increment /= n1*n2*n3*n4
                        absLocation = "%s/%s" % (outputFolder, location)
                        assert not os.path.isdir(file), "\n\nError: InstallBinariesToBuildFolder cannot install a folder (%s)" % file
                        os.path.exists(absLocation) or os.makedirs(absLocation)
                        assert os.path.exists(absLocation), "Could not create %s\n" % absLocation
                        fileResult = (0 != shutil.copy(file, absLocation))
                        result = fileResult and result
                        self.__NotifyListeners(ProgressEvent(self,progress))
                        if self.IsCanceled(): return False
                        progress += increment
                        if not fileResult:
                            message = "Failed to copy %s to %s\n" % (file, absLocation)
                            logger.error( message )
                        else:
                            logger.debug( "copied %s to %s" % (file, absLocation) )
                            
        return result

    def __NotifyListeners(self, event):
        """ Notify the attached listeners about the event. """
        for listener in self.__listeners:
            listener.Update(event)
        
    def AddListener(self, listener):
        """ Attach a listener to this class. """
        if not listener in self.__listeners:
            self.__listeners.append(listener)
