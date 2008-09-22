import os
import shutil
import csnUtility
import csnCompiler

class Compiler(csnCompiler.Compiler):
    def __init__(self):
        csnCompiler.Compiler.__init__(self)
        self.postProcessor = PostProcessor()

    def IsForPlatform(self, _WIN32, _NOT_WIN32):
        return _NOT_WIN32 or (not _WIN32 and not _NOT_WIN32)

    def GetOutputFolder(self, _configuration = "${CMAKE_CFG_INTDIR}"):
        """
        Returns the folder where the compiler places binaries for _configuration.
        The default value for _configuration returns the output folder for the current configuration.
        for storing binaries.
        """
        return "%s/bin/%s" % (self.GetBuildFolder(), _configuration)
        
class PostProcessor:
    def __GetKDevelopProjectFilename(self, _project, _folder = None):
        if _folder is None:
            return "%s/%s.kdevelop" % (_project.GetBuildFolder(), _project.name)
        else:
            return "%s/%s.kdevelop" % (_folder, _project.name)
        
    def __GetFilelistFilename(self, _project, _folder = None):
        return "%s.filelist" % self.__GetKDevelopProjectFilename(_project, _folder)
        
    def Do(self, _project, _binaryFolder, _kdevelopProjectFolder):
        if not os.path.exists(_kdevelopProjectFolder):
            # if _kdevelopProjectFolder does not exist, then it MUST equal "".
            # otherwise, the user specified an invalid path for _kdevelopProjectFolder.  
            assert _kdevelopProjectFolder == "", "Cannot create kdevelop files in %s. Folder does not exist." % _kdevelopProjectFolder 
            return
            
        kdevelopProjectFolder = csnUtility.NormalizePath(_kdevelopProjectFolder)

        if not os.path.exists(self.__GetKDevelopProjectFilename(_project)):
            return
            
        f = open(self.__GetFilelistFilename(_project), 'w')
        for project in _project.ProjectsToUse():
            for source in project.sources:
                fileListItem = csnUtility.RemovePrefixFromPath(source, kdevelopProjectFolder)
                fileListItem = csnUtility.NormalizePath(fileListItem)
                f.write(fileListItem + "/n")
        f.close()
        
        csnUtility.ReplaceDestinationFileIfDifferent(self.__GetFilelistFilename(_project, kdevelopProjectFolder), self.__GetFilelistFilename(_project))
        
        f = open(self.__GetKDevelopProjectFilename(_project), 'r')
        kdevelopProjectText = f.read()
        f.close()
        searchText = "<projectdirectory>%s" % _project.GetBuildFolder()
        replaceText = "<projectdirectory>%s" % kdevelopProjectFolder
        kdevelopProjectText = kdevelopProjectText.replace(searchText, replaceText)
        searchText = "<filelistdirectory>%s" % _project.GetBuildFolder()
        replaceText = "<filelistdirectory>%s" % kdevelopProjectFolder
        kdevelopProjectText = kdevelopProjectText.replace(searchText, replaceText)
        if csnUtility.FileToString(self.__GetKDevelopProjectFilename(_project, kdevelopProjectFolder)) != kdevelopProjectText:
            f = open(self.__GetKDevelopProjectFilename(_project, kdevelopProjectFolder), 'w')
            f.write(kdevelopProjectText)
            f.close()
