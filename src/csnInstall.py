import csnUtility
import os
import glob
import GlobDirectoryWalker

class Manager:
    def __init__(self, _project):
        self.project = _project
        self.filesToInstall = dict()
        self.filesToInstall["Debug"] = dict()
        self.filesToInstall["Release"] = dict()

    def AddFilesToInstall(self, _list, _location = None, _debugOnly = 0, _releaseOnly = 0, _WIN32 = 0, _NOT_WIN32 = 0):
        if not self.project.context.IsForPlatform(_WIN32, _NOT_WIN32):
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
                        path = csnUtility.NormalizePath(dllPattern)
                        if not os.path.isabs(path):
                            path = "%s/%s" % (self.project.context.thirdPartyBuildFolder, path)
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
 