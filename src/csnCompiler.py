
class CompileAndLinkSettings:
    """ 
    Helper class containing the settings that must be passed to the compiler and linker to build a target.
    """
    def __init__(self):
        self.definitions = list()
        self.libraries = list()
        self.includeFolders = list()
        self.libraryFolders = list()

class Compiler:
    def __init__(self):
        self.public = CompileAndLinkSettings()
        self.private = CompileAndLinkSettings()

    def GetConfig(self, _isPrivate):
        if _isPrivate:
            return self.private
        else:
            return self.public

    def SetBuildFolder(self, _buildFolder):
        self.buildFolder = _buildFolder

    def GetBuildFolder(self):
        return self.buildFolder
        
    def GetPostProcessor(self):
        return self.postProcessor
