import csnCompiler

class LinuxCommon(csnCompiler.Compiler):
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
        return "%s/%s/%s" % (_projectType, self.context.GetConfigurationName(), _projectName)

    def GetThirdPartySubFolder(self):
        return self.context.GetConfigurationName()
    
    def GetThirdPartyCMakeParameters(self):
        return [
            "-D", "CMAKE_BUILD_TYPE=" + self.context.GetConfigurationName(),
            "-D", "CMAKE_C_FLAGS=-fPIC",
            "-D", "CMAKE_CXX_FLAGS=-fPIC"
        ]
    
    def GetAllowedConfigurations(self):
        return ["Debug", "Release"]


