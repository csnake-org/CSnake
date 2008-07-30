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

    def SetBinFolder(self, _binFolder):
        self.binFolder = _binFolder

    def GetBinFolder(self):
        return self.binFolder
