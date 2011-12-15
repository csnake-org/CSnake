## @package csnLinuxCommon
# Definition of LinuxCommon csnCompiler.Compiler. 
# \ingroup compiler
import csnCompiler
import platform
import csnUtility

class LinuxCommon(csnCompiler.Compiler):
    """ Abstract Linux compiler. """
    def __init__(self):
        csnCompiler.Compiler.__init__(self)   
        #self.basicFields.append("kdevelopProjectFolder")
        
    def GetCompileFlags(self):
        return ["-fPIC"]
        
    def IsForPlatform(self, _WIN32, _NOT_WIN32):
        return (((not csnUtility.IsWindowsPlatform()) and _NOT_WIN32) # Unix match
            or (csnUtility.IsWindowsPlatform() and _WIN32) # Cygwin match
            or (not _WIN32 and not _NOT_WIN32)) # Nothing demanded

    def GetOutputSubFolder(self, _configuration = "${CMAKE_CFG_INTDIR}"):
        """
        Returns the folder where the compiler places binaries for _configuration.
        The default value for _configuration returns the output folder for the current configuration.
        for storing binaries.
        """
        return "bin/%s" % (_configuration)
    
    def GetBuildSubFolder(self, _projectType, _projectName):
        return "%s/%s/%s" % (_projectType, self._configurationName, _projectName)

    def GetThirdPartySubFolder(self):
        return self._configurationName
    
    def GetThirdPartyCMakeParameters(self):
        return [
            "-D", "CMAKE_BUILD_TYPE=" + self._configurationName,
            "-D", "CMAKE_C_FLAGS=-fPIC",
            "-D", "CMAKE_CXX_FLAGS=-fPIC"
        ]
    
    def GetAllowedConfigurations(self):
        return ["Debug", "Release"]
    
    def TargetIs32Bits(self):
        return platform.architecture()[0]=="32bit"
    
    def TargetIs64Bits(self):
        return platform.architecture()[0]=="64bit"
    
    def TargetIsMac(self):
        return csnUtility.IsMacPlatform()
    
    def TargetIsLinux(self):
        return csnUtility.IsLinuxPlatform()


