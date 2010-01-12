import csnContext
import csnCompiler
import os
import shutil
import csnUtility

class Common(csnCompiler.Compiler):
    def __init__(self):
        csnCompiler.Compiler.__init__(self)   
        #self.basicFields.append("kdevelopProjectFolder")
        
    def GetCompileFlags(self):
        return ["-fPIC"]
        
    def IsForPlatform(self, _WIN32, _NOT_WIN32):
        return _NOT_WIN32 or (not _WIN32 and not _NOT_WIN32)

    def GetOutputSubFolder(self, _configuration = "${CMAKE_CFG_INTDIR}"):
        """
        Returns the folder where the compiler places binaries for _configuration.
        The default value for _configuration returns the output folder for the current configuration.
        for storing binaries.
        """
        return "bin/%s" % (_configuration)
    
    def GetBuildSubFolder(self, _projectType, _projectName):
        return "%s/%s/%s" % (_projectType, self.context.configurationName, _projectName)

    def GetThirdPartySubFolder(self):
        return self.context.configurationName
    
    def GetThirdPartyCMakeParameters(self):
        return [
            "-D", "CMAKE_BUILD_TYPE=" + self.context.configurationName,
            "-D", "CMAKE_C_FLAGS=-fPIC",
            "-D", "CMAKE_CXX_FLAGS=-fPIC"
        ]
    
    def GetThirdPartyBuildFolder(self):
        # "os.path.join" would be better, but doesn't work in Windows because backslashes are not (yet) escaped by csnake
        return self.context.thirdPartyBuildFolder + "/" + self.context.configurationName
    
    def GetAllowedConfigurations(self):
        return ["Debug", "Release"]

class KDevelop(Common):
    def __init__(self):
        Common.__init__(self)
        self.postProcessor = KDevelopPostProcessor()

    def GetName(self):
        return "KDevelop3"
    
    def GetPostProcessor(self):
        return self.postProcessor

class Makefile(Common):
    def __init__(self):
        Common.__init__(self)

    def GetName(self):
        return "Unix Makefiles"
    
    def GetPostProcessor(self):
        return None
        
class KDevelopPostProcessor:
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
        
        #searchText = "<mainprogram>%s" % _project.GetBuildFolder()
        #replaceText = "<mainprogram>%s" % _project.context.GetOutputFolder(_project.context.configurationName)
        #kdevelopProjectText = kdevelopProjectText.replace(searchText, replaceText)
        
        if csnUtility.FileToString(self.__GetKDevelopProjectFilename(_project, kdevelopProjectFolder)) != kdevelopProjectText:
            f = open(self.__GetKDevelopProjectFilename(_project, kdevelopProjectFolder), 'w')
            f.write(kdevelopProjectText)
            f.close()
