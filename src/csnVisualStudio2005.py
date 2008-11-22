import csnCompiler

class Compiler(csnCompiler.Compiler):
    def __init__(self):
        csnCompiler.Compiler.__init__(self)
        self.private.definitions.append("/Zm200")        
        self.postProcessor = PostProcessor()

    def IsForPlatform(self, _WIN32, _NOT_WIN32):
        return _WIN32 or (not _WIN32 and not _NOT_WIN32)

    def GetOutputFolder(self, _configuration = "${CMAKE_CFG_INTDIR}"):
        """
        Returns the folder where the compiler places binaries for _configuration.
        The default value for _configuration returns the output folder for the current configuration.
        for storing binaries.
        """
        if _configuration == "DebugAndRelease":
            return "%s/bin" % self.GetBuildFolder()
        else:
            return "%s/bin/%s" % (self.GetBuildFolder(), _configuration)
        
class PostProcessor:
    def Do(self, _project, _binaryFolder, _kdevelopProjectFolder = "ignored"):
        """
        Post processes the vcproj file generated for _project, where the vc proj file was written
        to _binaryFolder.         
        """
        
        # print "Skip postprocessing of visual studio 2005 file"
        return
