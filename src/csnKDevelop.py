import csnContext
import csnProject
import os
import shutil
import csnUtility

class Context(csnContext.Context):
    def __init__(self):
        csnContext.Context.__init__(self)
        self.kdevelopProjectFolder = ""    
        self.basicFields.append("kdevelopProjectFolder")
        self.postProcessor = PostProcessor()
        
    def CreateProject(self, _name, _type, _sourceRootFolder = None, _categories = None):
        project = csnProject.GenericProject(_name, _type, _sourceRootFolder, _categories, _context = self)
	project.compileManager.private.definitions.append("-fPIC")
        return project
        
    def IsForPlatform(self, _WIN32, _NOT_WIN32):
        return _NOT_WIN32 or (not _WIN32 and not _NOT_WIN32)

    def GetOutputFolder(self, _configuration = "${CMAKE_CFG_INTDIR}"):
        """
        Returns the folder where the compiler places binaries for _configuration.
        The default value for _configuration returns the output folder for the current configuration.
        for storing binaries.
        """
        return "%s/bin/%s" % (self.buildFolder, _configuration)
        
class PostProcessor:
    def __GetKDevelopProjectFilename(self, _project, _folder = None):
        if _folder is None:
            return "%s/%s.kdevelop" % (_project.GetBuildFolder(), _project.name)
        else:
            return "%s/%s.kdevelop" % (_folder, _project.name)
        
    def __GetFilelistFilename(self, _project, _folder = None):
        return "%s.filelist" % self.__GetKDevelopProjectFilename(_project, _folder)
        
    def Do(self, _project):
        if not os.path.exists(_project.context.kdevelopProjectFolder):
            # if _kdevelopProjectFolder does not exist, then it MUST equal "".
            # otherwise, the user specified an invalid path for kdevelopProjectFolder.  
            assert _project.context.kdevelopProjectFolder == "", "\n\nError: Cannot create kdevelop files in %s. Folder does not exist." % _project.context.kdevelopProjectFolder
            return
            
        kdevelopProjectFolder = csnUtility.NormalizePath(_project.context.kdevelopProjectFolder)

        if not os.path.exists(self.__GetKDevelopProjectFilename(_project)):
            return
            
        f = open(self.__GetFilelistFilename(_project), 'w')
        for project in _project.dependenciesManager.ProjectsToUse():
            for source in project.GetSources():
                fileListItem = csnUtility.RemovePrefixFromPath(source, kdevelopProjectFolder)
                fileListItem = csnUtility.NormalizePath(fileListItem)
                f.write(fileListItem + "/n")
        f.close()
        
        csnUtility.ReplaceDestinationFileIfDifferent(self.__GetFilelistFilename(_project), self.__GetFilelistFilename(_project, kdevelopProjectFolder))
        
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
