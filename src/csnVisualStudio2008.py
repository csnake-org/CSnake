## @package csnVisualStudio2008
# Definition of the csnVisualStudio2008 compilers. 
import csnCompiler
import os

class Compiler(csnCompiler.Compiler):
    """ Abstract Visual Studio 2008 compiler. """
    def __init__(self):
        csnCompiler.Compiler.__init__(self)
        self.postProcessor = PostProcessor()
    
    def GetCompileFlags(self):
        return [""]
    
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
    
    def GetPostProcessor(self):
        return self.postProcessor
    
    def TargetIsMac(self):
        return False
    
    def TargetIsLinux(self):
        return False

class Compiler32(Compiler):
    """ Visual Studio 2008 32bits compiler. """
    def GetName(self):
        return "Visual Studio 9 2008"
    
    def TargetIs32Bits(self):
        return True
    
    def TargetIs64Bits(self):
        return False

class Compiler64(Compiler):
    """ Visual Studio 2008 64bits compiler. """
    def GetName(self):
        return "Visual Studio 9 2008 Win64"
    
    def TargetIs32Bits(self):
        return False
    
    def TargetIs64Bits(self):
        return True

class PostProcessor:
    def Do(self, _project):
        """
        Post processes the vcproj file generated for _project.
        """
        # vc proj to patch
        if not _project.dependenciesManager.isTopLevel:
            slnFilename = "%s/%s.sln" % (_project.GetBuildFolder(), _project.name)
            if os.path.exists(slnFilename):
                os.remove(slnFilename)

