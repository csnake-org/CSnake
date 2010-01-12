import csnCompiler
import os


class Compiler(csnCompiler.Compiler):
    def __init__(self):
        csnCompiler.Compiler.__init__(self)
        self.postProcessor = PostProcessor()

    def GetCompileFlags(self):
        return ["/Zm200"]

    def IsForPlatform(self, _WIN32, _NOT_WIN32):
        return _WIN32 or (not _WIN32 and not _NOT_WIN32)

    def GetOutputSubFolder(self, _configuration = "${CMAKE_CFG_INTDIR}"):
        """
        Returns the folder where the compiler should place binaries for _configuration.
        The default value for _configuration returns the output folder for the current configuration.
        for storing binaries.
        """
        if _configuration == "DebugAndRelease":
            return "bin"
        else:
            return "bin/%s" % (_configuration)
        
    def GetBuildSubFolder(self, _projectType, _projectName):
        return "%s/%s" % (_projectType, _projectName)
        
    def GetThirdPartySubFolder(self):
        return ""
    
    def GetThirdPartyCMakeParameters(self):
        return []
    
    def GetAllowedConfigurations(self):
        return ["DebugAndRelease"]
    
    def GetName(self):
        return "Visual Studio 8 2005"
    
    def GetPostProcessor(self):
        return self.postProcessor

class Compiler64(Compiler):
    def GetName(self):
        return "Visual Studio 8 2005 Win64"
        
class PostProcessor:
    def Do(self, _project):
        """
        Post processes the vcproj file generated for _project.
        """
        
        if not _project.dependenciesManager.isTopLevel:
            slnFilename = "%s/%s.sln" % (_project.GetBuildFolder(), _project.name)
            if os.path.exists(slnFilename):
                os.remove(slnFilename)
        return
