import os
import shutil
import csnUtility
import csnBuild

class Compiler:
    def __init__(self):
        self.public = csnBuild.CompileAndLinkSettings()
        self.private = csnBuild.CompileAndLinkSettings()

    def IsForPlatform(self, _WIN32, _NOT_WIN32):
        return _NOT_WIN32 or (not _WIN32 and not _NOT_WIN32)

    def GetConfig(self, _isPrivate):
        if _isPrivate:
            return self.private
        else:
            return self.public

class PostProcessor:
    def Do(self, _targetProject, _binaryFolder, _kdevelopProjectFolder):

        if not os.path.exists(_kdevelopProjectFolder):
            # if _kdevelopProjectFolder does not exist, then it MUST equal "".
            # otherwise, the user specified an invalid path for _kdevelopProjectFolder.  
            assert _kdevelopProjectFolder == "", "Cannot create kdevelop files in %s. Folder does not exist." % _kdevelopProjectFolder 
            return
            
        kdevelopProjectFolder = csnUtility.NormalizePath(_kdevelopProjectFolder)
        binaryProjectFolder = _targetProject.AbsoluteBinaryFolder(_binaryFolder)
        kdevProjectFilename = "%s/%s.kdevelop" % (binaryProjectFolder, _targetProject.name)
        kdevProjectFileListFilename = "%s.filelist" % kdevProjectFilename

        if not os.path.exists(kdevProjectFilename):
            return
            
        f = open(kdevProjectFileListFilename, 'w')
        for project in _targetProject.ProjectsToUse():
            for source in project.sources:
                fileListItem = csnUtility.NormalizePath(cnsUtility.RemovePrefixFromPath(fileListItem, kdevelopProjectFolder))
                f.write(fileListItem + "\n")
        f.close()
        result = (0 != shutil.copy(kdevProjectFileListFilename, _kdevelopProjectFolder))
        assert result, "Could not copy from %s to %s\n" % (kdevProjectFileListFilename, _kdevelopProjectFolder)
        
        kdevelopFileInTargetFolder = "%s/%s.kdevelop" % (kdevelopProjectFolder, _targetProject.name) 
        f = open(kdevProjectFilename, 'r')
        kdevelopProjectText = f.read()
        f.close()
        f = open(kdevelopFileInTargetFolder, 'w')
        searchText = "<projectdirectory>%s" % binaryProjectFolder
        replaceText = "<projectdirectory>%s" % kdevelopProjectFolder
        kdevelopProjectText = kdevelopProjectText.replace(searchText, replaceText)
        searchText = "<filelistdirectory>%s" % binaryProjectFolder
        replaceText = "<filelistdirectory>%s" % kdevelopProjectFolder
        kdevelopProjectText = kdevelopProjectText.replace(searchText, replaceText)
        f.write(kdevelopProjectText)
        f.close()
