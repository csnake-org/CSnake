import os
import subprocess
import sys
import shutil
import csnUtility
import csnBuild
import csnCilab
import glob
import RollbackImporter
import inspect
import string

class RootNotFound(IOError):
    pass

class NotARoot(IOError):
    pass

class TypeError(StandardError):
    pass
    
def CreateCSnakeFolder(_folder, _projectRoot):
    # check that project root exists
    if not os.path.exists(_projectRoot):
        raise RootNotFound, "Root folder %s not found." % (_projectRoot)

    # check that project root is a root of _folder
    if( len(os.path.commonprefix([_folder, _projectRoot])) != len(_projectRoot) ):
        raise NotARoot, "%s is is not a root for %s" % (_folder, _projectRoot)
        
    # create _folder, and create __init__.py files in the subtree between _projectRoot and _folder
    os.path.exists(_folder) or os.makedirs(_folder)
    while not os.path.normpath(_folder) == os.path.normpath(_projectRoot):
        initFile = "%s/__init__.py" % (_folder)
        if not os.path.exists(initFile):
            f = open(initFile, 'w')
            f.write( "# Do not remove. Used to find python packages.\n" )
            f.close()
        _folder = os.path.dirname(_folder)

def CreateCSnakeProject(_folder, _projectRoot, _name, _type):
    """ 
    _name - name of the project (e.g. TestLib)
    _type - should be 'executable', 'dll', or 'library' 
    """
    types = ['executable', 'dll', 'library']
    if not _type in types:
        raise TypeError, "Type should be 'executable', 'dll' or 'library'"
        
    CreateCSnakeFolder(_folder, _projectRoot)
    
    nameList = list(_name)
    instanceName = nameList[0].lower() + ''.join(nameList[1:])
    filename = "%s/csn%s.py" % (_folder, _name)
    
    if os.path.exists(filename):
        raise IOError, "Project file %s already exists\n" % (filename)
        
    f = open(filename, 'w')
    f.write( "# Used to configure %s\n" % (_name) )
    f.write( "import csnBuild\n" )
    f.write( "%s = csnBuild.Project(\"%s\", \"%s\")\n" % (instanceName, _name, _type) )
    f.write( "%s.AddSources([\"src/*.h\", \"src/*.cpp\"]) # note: argument must be a python list!\n" % (instanceName) )
    f.write( "%s.AddIncludeFolders([\"src\"]) # note: argument must be a python list!\n" % (instanceName) )
    f.close()

class RollbackHandler:
    """
    This helper class instantiates the RollbackImporter and extends the python search path 
    """
    def SetUp(self, _projectPath, _sourceRootFolders, _thirdPartyRootFolder):
        """
        Set up the roll back. 
        """
        # set up roll back of imported modules
        self.rbi = RollbackImporter.RollbackImporter()
        self.previousPaths = list(sys.path)
        
        # extend python path with project folder, source root and third party root
        newPaths = list(_sourceRootFolders)
        newPaths.extend([_projectPath, _thirdPartyRootFolder]) 
        for path in newPaths:
            if not path in sys.path:
                sys.path.append(path)
    
    def TearDown(self):
        """
        Execute roll back. 
        """
        # roll back imported modules
        self.rbi.rollbackImports()

        # undo additions to the python path
        sys.path = list(self.previousPaths)
                    
class Handler:
    def __init__(self):
        self.cmakePath = ""
        self.pythonPath = ""
        self.cmakeFound = 0 
        self.cmakeBuildType = "None"
        pass
    
    def SetCMakePath(self, _cmakePath):
        if not self.cmakePath == _cmakePath:
            self.cmakePath = _cmakePath
            self.cmakeFound = self.CMakeIsFound() 
            if self.cmakeFound:
                print "CMake was found.\n"
        if not self.cmakeFound:
            print "Warning: %s is is not a valid path to cmake. Select path to CMake using menu Settings->Edit Settings." % self.cmakePath
        return self.cmakeFound
        
    def SetPythonPath(self, path):
        csnBuild.pythonPath = path
        if not (os.path.exists(csnBuild.pythonPath) and os.path.isfile(csnBuild.pythonPath)):
            print "Warning: python not found at: %s. Check the path in the Options menu.\n" % csnBuild.pythonPath
        
        return 1
        
    def SetCompiler(self, _compiler):
        self.compiler = _compiler
        
    def SetCMakeBuildType(self, _buildType):
        self.cmakeBuildType = _buildType
        
    def __DeleteTopLevelPycFile(self, _settings):
        (projectFolder, name) = os.path.split(_settings.csnakeFile)
        (name, ext) = os.path.splitext(name)

        pycFilename = os.path.join(projectFolder, name + ".pyc")
        if os.path.exists(pycFilename):
            os.remove(pycFilename)
            print "Removed %s\n" % pycFilename
    
    def __GetProjectInstance(self, _settings):
        """ Instantiates and returns the _instance in _projectPath. """

        self.__DeleteTopLevelPycFile(_settings)
        
        # set up roll back of imported modules
        rollbackHandler = RollbackHandler()
        rollbackHandler.SetUp(_settings.csnakeFile, _settings.rootFolders, _settings.thirdPartyRootFolder)
        
        csnCilab.thirdPartyModuleFolder = _settings.thirdPartyRootFolder
        csnCilab.thirdPartyBinFolder = _settings.thirdPartyBinFolder
        
        (projectFolder, name) = os.path.split(_settings.csnakeFile)
        (name, ext) = os.path.splitext(name)
        
        try:
            project = csnUtility.LoadModule(projectFolder, name)   
            exec "instance = project.%s" % _settings.instance
        finally:
            # undo additions to the python path
            rollbackHandler.TearDown()

        return instance
    
    def ConfigureProjectToBinFolder(self, _settings, _alsoRunCMake):
        logString = ""
        instance = self.__GetProjectInstance(_settings)
        
        generator = csnBuild.Generator()
        instance.ResolvePathsOfFilesToInstall(_settings.thirdPartyBinFolder)
        generator.Generate(instance, _settings.binFolder, _settings.installFolder, self.cmakeBuildType)
            
        if _alsoRunCMake:
            if not self.cmakeFound:
                print "Please specify correct path to CMake"
                return
                
            folderCMakeLists = "%s/%s/" % (_settings.binFolder, instance.cmakeListsSubpath)
            argList = [self.cmakePath, "-G", self.compiler, folderCMakeLists]
            retcode = subprocess.Popen(argList, cwd = _settings.binFolder).wait()
            if retcode == 0:
                generator.PostProcess(instance, _settings.binFolder)
            else:
                print "Configuration failed.\n"   
            
    def InstallThirdPartyBinariesToBinFolder(self, _settings):
        """ 
        This function copies all third party dlls to the binary folder, so that you can run the executables in the
        binary folder without having to build the INSTALL target.
        """
        instance = self.__GetProjectInstance(_settings)
        folders = dict()
        folders["debug"] = "%s/bin/Debug" % _settings.binFolder
        folders["release"] = "%s/bin/Release" % _settings.binFolder

        instance.ResolvePathsOfFilesToInstall(_settings.thirdPartyBinFolder)
        for mode in ("debug", "release"):
            os.path.exists(folders[mode]) or os.makedirs(folders[mode])
            for project in instance.AllProjects(_recursive = 1):
                for location in project.filesToInstall[mode].keys():
                    for file in project.filesToInstall[mode][location]:
                        absLocation = "%s/%s" % (folders[mode], location)
                        os.path.exists(absLocation) or os.makedirs(absLocation)
                        shutil.copy(file, absLocation)
             
    def CMakeIsFound(self):
        found = os.path.exists(self.cmakePath) and os.path.isfile(self.cmakePath)
        if not found:
            try:
                retcode = subprocess.Popen(self.cmakePath).wait()
            except:
                retcode = 1
            found = retcode == 0
        return found
    
    def ConfigureThirdPartyFolder(self, _settings):
        """ 
        Runs cmake to install the libraries in the third party folder.
        """
        result = 1
        messageAboutPatches = ""
        
        if not self.cmakeFound:
            print "Please specify correct path to CMake"
            return 0
        
        # apply MITK patch
        originalMITK = "%s/MITK-0.7/MITK-0.7Config.cmake.in" % _settings.thirdPartyRootFolder
        patchedMITK = "%s/MITK-0.7/MITK-0.7Config.cmake.in.patchedForCSnake" % _settings.thirdPartyRootFolder
        if not os.path.exists(patchedMITK):
            print "Warning: patch failed. File not found: %s\n" % patchedMITK
            result = 1
        else:
            shutil.copy(patchedMITK, originalMITK)
            messageAboutPatches = "Note: Applied patch to file %s\n" % originalMITK
        
        # apply ITK patch
        if result:
            originalITK = "%s/ITK-3.2/InsightToolkit-3.2.0/UseITK.cmake.in" % _settings.thirdPartyRootFolder
            patchedITK = "%s/ITK-3.2/InsightToolkit-3.2.0/UseITK.cmake.in.patchedForCSnake" % _settings.thirdPartyRootFolder
            if not os.path.exists(patchedITK):
                print "Warning: patch failed. File not found: %s\n" % patchedITK
                result = 1
            else:
                shutil.copy(patchedITK, originalITK)
                messageAboutPatches = messageAboutPatches + "Note: Applied patch to file %s\n" % originalITK
        
        if result:
            os.path.exists(_settings.thirdPartyBinFolder) or os.makedirs(_settings.thirdPartyBinFolder)
            argList = [self.cmakePath, "-G", self.compiler, _settings.thirdPartyRootFolder]
            retcode = subprocess.Popen(argList, cwd = _settings.thirdPartyBinFolder).wait()
            if retcode:
                retcode = subprocess.Popen(argList, cwd = _settings.thirdPartyBinFolder).wait()
            if not retcode == 0:
                result = 0
                print "Configuration failed.\n"   
            
        print messageAboutPatches
        return result

    def DeletePycFiles(self, _settings, _onlyThirdPartyRootFolder = 0):
        """
        Tries to delete all pyc files from _projectPath, _sourceRootFolders, thirdPartyRootFolder and 
        all base folders where the CSnake files for building _instance are. 
        However, __init__.pyc files are not removed.
        """
        # determine list of folders to search for pyc files
        folderList = list(_settings.thirdPartyRootFolder)
        
        if not _onlyThirdPartyRootFolder:
            folderList.extend(_settings.rootFolders)
            folderList.append(_settings.csnakeFile)
            instance = self.__GetProjectInstance(_settings)
            for project in instance.AllProjects(_recursive = 1):
                folderList.append(project.sourceRootFolder)
                    
        # remove pyc files
        for folder in folderList:
            pattern = "%s/*.pyc" % folder
            pycFiles = [x.replace("\\", "/") for x in glob.glob(pattern)]
            for pycFile in pycFiles:
                if not os.path.basename(pycFile) == "__init__.pyc":
                    os.remove(pycFile)

        # remove more pyc files from the third party root folder
        for pycFile in [x.replace("\\", "/") for x in glob.glob("%s/*/*.pyc" % _settings.thirdPartyRootFolder)]:
            if not os.path.basename(pycFile) == "__init__.pyc":
                os.remove(pycFile)
     
    def GetListOfPossibleTargets(self, _settings):
        """
        Returns a list of possible targets which are defined in CSnake file _projectPath.
        """
        
        self.__DeleteTopLevelPycFile(_settings)
        
        rollbackHandler = RollbackHandler()
        rollbackHandler.SetUp(_settings.csnakeFile, _settings.rootFolders, _settings.thirdPartyRootFolder)
        result = []

        # find csnake targets in the loaded module
        (projectFolder, name) = os.path.split(_settings.csnakeFile)
        (name, ext) = os.path.splitext(name)
        csnCilab.thirdPartyModuleFolder = _settings.thirdPartyRootFolder
        project = csnUtility.LoadModule(projectFolder, name)   
        for member in inspect.getmembers(project):
            if isinstance(member[1], csnBuild.Project):
                result.append(member[0])
        
        rollbackHandler.TearDown()
        return result
        
    def GetListOfSpuriousPluginDlls(self, _settings):
        """
        Determines a list of GIMIAS plugin dlls that were found in _settings.binFolder, and returns a list of filenames containing those 
        plugin dlls which are not built by the current configuration (in _settings).
        """
        result = []
        instance = self.__GetProjectInstance(_settings)
        if not instance.name.lower() == "gimias":
            return result
    
        configuredPluginNames = [project.name for project in instance.AllProjects(_recursive = 1) ]
        for configuration in ("Debug", "Release"):
            pluginsFolder = "%s/bin/%s/plugins/*" % (_settings.binFolder, configuration)

            for pluginFolder in glob.glob( pluginsFolder ):
                pluginName = os.path.basename(pluginFolder)
                if not os.path.isdir(pluginFolder) or pluginName in configuredPluginNames:
                    continue
                    
                searchPath = string.Template("$folder/lib/$config/$name.dll").substitute(folder = pluginFolder, config = configuration, name = pluginName )
                if os.path.exists( searchPath ):
                    result.append( searchPath )
                    
        return result

    def GetTargetSolutionPath(self, _settings):
        instance = self.__GetProjectInstance(_settings)
        binaryProjectFolder = _settings.binFolder + "/" + instance.binarySubfolder
        return "%s/%s.sln" % (binaryProjectFolder, instance.name)

    def GetThirdPartySolutionPath(self, _settings):
        return "%s/CILAB_TOOLKIT.sln" % (_settings.thirdPartyBinFolder)
