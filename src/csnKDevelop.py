## @package csnKDevelop
# Definition of Linux csnCompiler.Compiler. 
# \ingroup compiler
import os
import csnUtility
from csnLinuxCommon import LinuxCommon

class Makefile(LinuxCommon):
    """ Makefile compiler. """
    def __init__(self):
        LinuxCommon.__init__(self)

    def GetName(self):
        return "Unix Makefiles"
    
    def GetPostProcessor(self):
        return None

class Eclipse(LinuxCommon):
    """ Eclipse compiler. """
    def __init__(self):
        LinuxCommon.__init__(self)

    def GetName(self):
        return "Eclipse CDT4 - Unix Makefiles"
    
    def GetPostProcessor(self):
        return None

class KDevelop(LinuxCommon):
    """ KDevelop compiler. """
    def __init__(self):
        LinuxCommon.__init__(self)
        self.postProcessor = KDevelopPostProcessor()

    def GetName(self):
        return "KDevelop3"
    
    def GetPostProcessor(self):
        return self.postProcessor
        
class KDevelopPostProcessor:
    def __GetKDevelopProjectFilename(self, _project, _folder = None):
        if _folder is None:
            return "%s/%s.kdevelop" % (_project.GetBuildFolder(), _project.name)
        else:
            return "%s/%s.kdevelop" % (_folder, _project.name)
        
    def __GetFilelistFilename(self, _project, _folder = None):
        return "%s.filelist" % self.__GetKDevelopProjectFilename(_project, _folder)
        
    def Do(self, _project):
        # create folder if it does not exist
        if not os.path.exists(_project.context.GetKdevelopProjectFolder()):
            os.makedirs(_project.context.GetKdevelopProjectFolder())
            
        kdevelopProjectFolder = csnUtility.NormalizePath(_project.context.GetKdevelopProjectFolder())

        if not os.path.exists(self.__GetKDevelopProjectFilename(_project)):
            return
        
        # Postprocess "*.kdevelop.filelist" file (KDevelop filelist)
        
        f = open(self.__GetFilelistFilename(_project), 'w')
        for project in _project.dependenciesManager.ProjectsToUse():
            for source in project.GetSources():
                fileListItem = csnUtility.RemovePrefixFromPath(source, kdevelopProjectFolder)
                fileListItem = csnUtility.NormalizePath(fileListItem)
                f.write(fileListItem + "/n")
        f.close()
        
        csnUtility.ReplaceDestinationFileIfDifferent(self.__GetFilelistFilename(_project), self.__GetFilelistFilename(_project, kdevelopProjectFolder))
        
        # Postprocess "*.kdevelop" file (KDevelop project)
        
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
