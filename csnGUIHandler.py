import os
import subprocess
import sys
import shutil
import csnUtility
import csnBuild
import csnCilab
import glob
import RollbackImporter

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
                
class Handler:
    def __init__(self):
        self.cmakePath = ""
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
        
    def SetCompiler(self, _compiler):
        self.compiler = _compiler
        
    def SetCMakeBuildType(self, _buildType):
        self.cmakeBuildType = _buildType
        
    def __GetProjectInstance(self, _projectPath, _instance, _sourceRootFolders, _thirdPartyRootFolder, _thirdPartyBinFolder):
        """ Instantiates and returns the _instance in _projectPath. """
        
        # set up roll back of imported modules
        rbi = RollbackImporter.RollbackImporter()
        previousPaths = sys.path
        
        (projectFolder, name) = os.path.split(_projectPath)
        (name, ext) = os.path.splitext(name)
        csnCilab.thirdPartyModuleFolder = _thirdPartyRootFolder
        csnCilab.thirdPartyBinFolder = _thirdPartyBinFolder
        
        # extend python path with project folder, source root and third party root
        newPaths = _sourceRootFolders
        newPaths.extend([_projectPath, _thirdPartyRootFolder]) 
        for path in newPaths:
            if not path in sys.path:
                sys.path.append(path)
        
        project = csnUtility.LoadModule(projectFolder, name)   
        exec "instance = project.%s" % _instance

        # undo additions to the python path
        sys.path = previousPaths
            
        # roll back imported modules
        rbi.rollbackImports()
        
        return instance
    
    def ConfigureProjectToBinFolder(self, _projectPath, _instance, _sourceRootFolders, _binFolder, _installFolder, _thirdPartyRootFolder, _thirdPartyBinFolder, _alsoRunCMake):
        logString = ""
        instance = self.__GetProjectInstance(_projectPath, _instance, _sourceRootFolders, _thirdPartyRootFolder, _thirdPartyBinFolder)
        
        generator = csnBuild.Generator()
        instance.ResolvePathsOfFilesToInstall(_thirdPartyBinFolder)
        generator.Generate(instance, _binFolder, _installFolder, self.cmakeBuildType)
            
        if _alsoRunCMake:
            if not self.cmakeFound:
                print "Please specify correct path to CMake"
                return
                
            folderCMakeLists = "%s/%s/" % (_binFolder, instance.cmakeListsSubpath)
            argList = [self.cmakePath, "-G", self.compiler, folderCMakeLists]
            retcode = subprocess.Popen(argList, cwd = _binFolder).wait()
            if retcode == 0:
                generator.PostProcess(instance, _binFolder)
            else:
                print "Configuration failed.\n"   
            
    def InstallThirdPartyBinariesToBinFolder(self, _projectPath, _instance, _sourceRootFolders, _binFolder, _thirdPartyRootFolder, _thirdPartyBinFolder):
        """ 
        This function copies all third party dlls to the binary folder, so that you can run the executables in the
        binary folder without having to build the INSTALL target.
        """
        instance = self.__GetProjectInstance(_projectPath, _instance, _sourceRootFolders, _thirdPartyRootFolder, _thirdPartyBinFolder)
        folders = dict()
        folders["debug"] = "%s/bin/Debug" % _binFolder
        folders["release"] = "%s/bin/Release" % _binFolder

        instance.ResolvePathsOfFilesToInstall(_thirdPartyBinFolder)
        for mode in ("debug", "release"):
            os.path.exists(folders[mode]) or os.makedirs(folders[mode])
            for project in instance.AllProjects(_recursive = 1):
                for location in project.filesToInstall[mode].keys():
                    for file in project.filesToInstall[mode][location]:
                        absLocation = "%s/%s" % (folders[mode], location)
                        os.path.exists(absLocation) or os.makedirs(absLocation)
                        shutil.copy(file, absLocation)
             
    def CMakeIsFound(self):
        found = os.path.exists(self.cmakePath)
        if not found:
            try:
                retcode = subprocess.Popen(self.cmakePath).wait()
            except:
                retcode = 1
            found = retcode == 0
        return found
    
    def ConfigureThirdPartyFolder(self, _thirdPartyRootFolder, _thirdPartyBinFolder):
        """ 
        Runs cmake to install the libraries in the third party folder.
        """
        result = 1
        messageAboutPatches = ""
        
        if not self.cmakeFound:
            print "Please specify correct path to CMake"
            return 0
        
        # apply MITK patch
        originalMITK = "%s/MITK-0.7/MITK-0.7Config.cmake.in" % _thirdPartyRootFolder
        patchedMITK = "%s/MITK-0.7/MITK-0.7Config.cmake.in.patchedForCSnake" % _thirdPartyRootFolder
        if not os.path.exists(patchedMITK):
            print "Warning: patch failed. File not found: %s\n" % patchedMITK
            result = 1
        else:
            shutil.copy(patchedMITK, originalMITK)
            messageAboutPatches = "Note: Applied patch to file %s\n" % originalMITK
        
        # apply ITK patch
        if result:
            originalITK = "%s/ITK-3.2/InsightToolkit-3.2.0/UseITK.cmake.in" % _thirdPartyRootFolder
            patchedITK = "%s/ITK-3.2/InsightToolkit-3.2.0/UseITK.cmake.in.patchedForCSnake" % _thirdPartyRootFolder
            if not os.path.exists(patchedITK):
                print "Warning: patch failed. File not found: %s\n" % patchedITK
                result = 1
            else:
                shutil.copy(patchedITK, originalITK)
                messageAboutPatches = messageAboutPatches + "Note: Applied patch to file %s\n" % originalITK
        
        if result:
            os.path.exists(_thirdPartyBinFolder) or os.makedirs(_thirdPartyBinFolder)
            argList = [self.cmakePath, "-G", self.compiler, _thirdPartyRootFolder]
            retcode = subprocess.Popen(argList, cwd = _thirdPartyBinFolder).wait()
            if retcode:
                retcode = subprocess.Popen(argList, cwd = _thirdPartyBinFolder).wait()
            if not retcode == 0:
                result = 0
                print "Configuration failed.\n"   
            
        print messageAboutPatches
        return result

    def DeletePycFiles(self, _projectPath = "", _instance = "", _sourceRootFolders = [], _thirdPartyRootFolder = ""):
        """
        Tries to delete all pyc files from _projectPath, _sourceRootFolders, thirdPartyRootFolder and 
        all base folders where the CSnake files for building _instance are. 
        However, __init__.pyc files are not removed.
        """
        # determine list of folders to search for pyc files
        folderList = []
        folderList.append(_thirdPartyRootFolder)
        
        if _instance != "":
            folderList.extend(_sourceRootFolders)
            folderList.append(_projectPath)
            instance = self.__GetProjectInstance(_projectPath, _instance, _sourceRootFolders, _thirdPartyRootFolder, _thirdPartyBinFolder = "")
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
        for pycFile in [x.replace("\\", "/") for x in glob.glob("%s/*/*.pyc" % _thirdPartyRootFolder)]:
            if not os.path.basename(pycFile) == "__init__.pyc":
                os.remove(pycFile)
     