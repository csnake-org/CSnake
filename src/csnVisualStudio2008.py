import csnContext
import csnProject

class Context(csnContext.Context):
    def __init__(self):
        csnContext.Context.__init__(self)
        self.postProcessor = PostProcessor()
        
    def CreateProject(self, _name, _type, _sourceRootFolder = None, _categories = None):
        project = csnProject.GenericProject(_name, _type, _sourceRootFolder, _categories, _context = self)
        project.compileManager.private.definitions.append("/Zm200")        
        return project

    def IsForPlatform(self, _WIN32, _NOT_WIN32):
        return _WIN32 or (not _WIN32 and not _NOT_WIN32)

    def GetOutputFolder(self, _configuration = "${CMAKE_CFG_INTDIR}"):
        """
        Returns the folder where the compiler should place binaries for _configuration.
        The default value for _configuration returns the output folder for the current configuration.
        for storing binaries.
        """
        if _configuration == "DebugAndRelease":
            return "%s/bin" % self.buildFolder
        else:
            return "%s/bin/%s" % (self.buildFolder, _configuration)
        
class PostProcessor:
    def Do(self, _project):
        """
        Post processes the vcproj file generated for _project, where the vc proj file was written
        to _binaryFolder.         
        """
        
        if not _project.dependenciesManager.isTopLevel:
            slnFilename = "%s/%s.sln" % (_project.GetBuildFolder(), _project.name)
            if os.path.exists(slnFilename):
                os.remove(slnFilename)
        return
