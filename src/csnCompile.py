import csnUtility
import os

class CompileAndLinkSettings:
    """ 
    Helper class containing the settings that must be passed to the compiler and linker to build a target.
    """
    def __init__(self):
        self.definitions = list()
        self.libraries = list()
        self.includeFolders = list()
        self.libraryFolders = list()

class Manager:
    def __init__(self, _project):
        self.project = _project
        self.sources = []
        self.sourceGroups = dict()
        self.sourcesToBeMoced = []
        self.sourcesToBeUIed = []
        self.public = CompileAndLinkSettings()
        self.private = CompileAndLinkSettings()
        self.precompiledHeader = ""
        self.generateWin32Header = 1
 
    def AddSources(self, _listOfSourceFiles, _moc = 0, _ui = 0, _sourceGroup = "", _checkExists = 1, _forceAdd = 0):
        for sourceFile in _listOfSourceFiles:
            sources = self.project.Glob(sourceFile)
            if _checkExists and not len(sources):
                    raise IOError, "Path file not found %s" % (sourceFile)
            if not len(sources) and _forceAdd:
                sources = [sourceFile]
            
            for source in sources:
                if _moc and not source in self.sourcesToBeMoced:
                    self.sourcesToBeMoced.append(source)
                
                if not source in self.sources:
                    if _ui:
                        self.sourcesToBeUIed.append(source)
                    self.sources.append(source)
                    if _sourceGroup != "":
                        if not self.sourceGroups.has_key(_sourceGroup):
                            self.sourceGroups[_sourceGroup] = []
                        self.sourceGroups[_sourceGroup].append(source)
                   
    def RemoveSources(self, _listOfSourceFiles):
        for sourceFile in _listOfSourceFiles:
            sources = self.project.Glob(sourceFile)
            if not len(sources):
                sources = [sourceFile]
            
            for source in sources:
                if source in self.sourcesToBeMoced:
                    self.sourcesToBeMoced.remove(source)
                
                if source in self.sources:
                    if source in self.sourcesToBeUIed:
                        self.sourcesToBeUIed.remove(source)
                    self.sources.remove(source)
                    for sourceGroupKey in self.sourceGroups.keys():
                        if source in self.sourceGroups[sourceGroupKey]:
                            self.sourceGroups[sourceGroupKey].remove(source)

    def AddIncludeFolders(self, _listOfIncludeFolders, _WIN32 = 0, _NOT_WIN32 = 0):
        """
        Adds items to self.publicIncludeFolders. 
        If an item has a relative path, then it will be prefixed with _sourceRootFolder.
        Added include paths must exist on the filesystem.
        If an item in _listOfIncludeFolders has wildcards, all matching folders will be added to the list.
        """
        if not self.project.context.IsForPlatform(_WIN32, _NOT_WIN32):
            return
        for includeFolder in _listOfIncludeFolders:
            for folder in self.project.Glob(includeFolder):
                if (not os.path.exists(folder)) or os.path.isdir(folder):
                    self.public.includeFolders.append( folder )

    def AddLibraryFolders(self, _listOfLibraryFolders, _WIN32 = 0, _NOT_WIN32 = 0):
        """
        Adds items to self.publicLibraryFolders. 
        If an item has a relative path, then it will be prefixed with _sourceRootFolder.
        Added library paths must exist on the filesystem.
        """
        if not self.project.context.IsForPlatform(_WIN32, _NOT_WIN32):
            return
        for libraryFolder in _listOfLibraryFolders:
            self.public.libraryFolders.append( self.__FindPath(libraryFolder) )

    def AddLibraries(self, _listOfLibraries, _WIN32 = 0, _NOT_WIN32 = 0, _debugOnly = 0, _releaseOnly = 0):
        """
        Adds items to self.publicLibraries. 
        _WIN32 -- Only for Windows platforms.
        _NOT_WIN32 -- Only for non-Windows platforms.
        _debug -- Only for the Debug configuration.
        _release  -- Only for the Release configuration.
        """
        if not self.project.context.IsForPlatform(_WIN32, _NOT_WIN32):
            return
            
        assert not( _debugOnly and _releaseOnly)
        type = "" # empty string is the default, meaning both debug and release
        if _debugOnly:
            type = "debug"
        if _releaseOnly:
            type = "optimized"

        for library in _listOfLibraries:
            self.public.libraries.append("%s %s" % (type, library))
 
    def __FindPath(self, _path):
        """ 
        Tries to locate _path as an absolute path or as a path relative to self.sourceRootFolder. 
        Returns an absolute path, containing only forward slashes.
        Throws IOError if path was not found.
        """
        path = os.path.normpath(_path)
        if not os.path.isabs(path):
            path = os.path.abspath("%s/%s" % (self.project.GetSourceRootFolder(), path))
        if not os.path.exists(path):
            raise IOError, "Path file not found %s (tried %s)" % (_path, path)
            
        path = csnUtility.NormalizePath(path)
        return path

    def AddDefinitions(self, _listOfDefinitions, _private = 0, _WIN32 = 0, _NOT_WIN32 = 0 ):
        """
        _private -- Don't propagate these definitions to dependency projects.
        _WIN32 -- Only for Windows platforms.
        _NOT_WIN32 -- Only for non-Windows platforms.
        """
        if not self.project.context.IsForPlatform(_WIN32, _NOT_WIN32):
            return
        self.project.GetConfig(_private).definitions.extend(_listOfDefinitions)

    def SetPrecompiledHeader(self, _precompiledHeader):
        """
        If _precompiledHeader is not "", then precompiled headers are used in Visual Studio (Windows) with
        this filename. 
        """
        globResult = self.project.Glob(_precompiledHeader)
        assert len(globResult) == 1, "\n\n%s: Error locating precompiled header file %s (source root folder = %s)" % (self.project.name, _precompiledHeader, self.project.GetSourceRootFolder())
        self.precompiledHeader = globResult[0]
        self.AddSources([_precompiledHeader], _sourceGroup = "PCH Files (header)")

    def GenerateWin32Header(self):
        """
        Generates the ProjectNameWin32.h header file for exporting/importing dll functions.
        """
        templateFilename = csnUtility.GetRootOfCSnake() + "/resources/Win32Header.h"
        if self.project.type == "library":
            templateFilename = csnUtility.GetRootOfCSnake() + "/resources/Win32Header.lib.h"
        templateOutputFilename = "%s/%sWin32Header.h" % (self.project.GetBuildFolder(), self.project.name)
        
        assert os.path.exists(templateFilename), "\n\nError: File not found %s\n" % (templateFilename)
        f = open(templateFilename, 'r')
        template = f.read()
        template = template.replace('${PROJECTNAME_UPPERCASE}', self.project.name.upper())
        template = template.replace('${PROJECTNAME}', self.project.name)
        f.close()
        
        # don't overwrite the existing file if it contains the same text, because this will trigger a source recompile later!
        if csnUtility.FileToString(templateOutputFilename) != template:
            f = open(templateOutputFilename, 'w')
            f.write(template)
            f.close()
