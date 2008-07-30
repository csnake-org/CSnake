import csnBuild

class Compiler:
    def __init__(self):
        self.public = csnBuild.CompileAndLinkSettings()
        self.private = csnBuild.CompileAndLinkSettings()

    def GetConfig(self, _isPrivate):
        if _isPrivate:
            return self.private
        else:
            return self.public

    def SetBuildFolder(self, _buildFolder):
        self.buildFolder = _buildFolder

    def GetBuildFolder(self):
        return self.buildFolder
        