import os
import sys
import shutil
import csnUtility
import csnBuild
import csnCilab
import glob

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
    f.write( "%s.AddPublicIncludeFolders([\"src\"]) # note: argument must be a python list!\n" % (instanceName) )
    f.close()
                
class Handler:
    def __init__(self):
        pass        
        
    def Test():
        pass
        
    def __GetProjectInstance(self, _projectPath, _instance, _sourceRootFolder, _thirdPartyRootFolder, _thirdPartyBinFolder):
        """ Instantiates and returns the _instance in _projectPath. """
        (projectFolder, name) = os.path.split(_projectPath)
        (name, ext) = os.path.splitext(name)
        csnCilab.thirdPartyModuleFolder = _thirdPartyRootFolder + "/thirdParty"
        csnCilab.thirdPartyBinFolder = _thirdPartyBinFolder
        
        # extend python path with project folder, source root and third party root
        addedToPythonPath = set()
        for path in (_projectPath, _sourceRootFolder, _thirdPartyRootFolder):
            if not path in sys.path:
                sys.path.append(path)
                addedToPythonPath.add(path)
    
        project = csnUtility.LoadModule(projectFolder, name)   
        exec "instance = project.%s" % _instance

        # undo additions to the python path
        for path in addedToPythonPath:
            sys.path.remove(path)
            
        return instance
        
    def ConfigureProjectToBinFolder(self, _projectPath, _instance, _sourceRootFolder, _binFolder, _installFolder, _thirdPartyRootFolder, _thirdPartyBinFolder, _alsoRunCMake):
        logString = ""
        instance = self.__GetProjectInstance(_projectPath, _instance, _sourceRootFolder, _thirdPartyRootFolder, _thirdPartyBinFolder)
        generator = csnBuild.Generator()
        instance.ResolvePathsOfFilesToInstall(_thirdPartyBinFolder)
        generator.Generate(instance, _binFolder, _installFolder)
            
        if _alsoRunCMake:
            folderCMakeLists = "%s/%s/" % (_binFolder, instance.cmakeListsSubpath)
            os.chdir(_binFolder)
            print os.popen('cmake %s' % folderCMakeLists).read()
            
    def InstallThirdPartyBinariesToBinFolder(self, _projectPath, _instance, _sourceRootFolder, _binFolder, _thirdPartyRootFolder, _thirdPartyBinFolder):
        """ 
        This function copies all third party dlls to the binary folder, so that you can run the executables in the
        binary folder without having to build the INSTALL target.
        """
        instance = self.__GetProjectInstance(_projectPath, _instance, _sourceRootFolder, _thirdPartyRootFolder, _thirdPartyBinFolder)
        folders = dict()
        folders["debug"] = "%s/bin/Debug" % _binFolder
        folders["release"] = "%s/bin/Release" % _binFolder

        instance.ResolvePathsOfFilesToInstall(_thirdPartyBinFolder)
        for mode in ("debug", "release"):
            os.path.exists(folders[mode]) or os.makedirs(folders[mode])
            for project in instance.GetProjectsToUse():
                # print "%s\n" % project.name
                for location in project.filesToInstall[mode].keys():
                    for file in project.filesToInstall[mode][location]:
                        absLocation = "%s/%s" % (folders[mode], location)
                        # print "Copy %s to %s\n" % (file, absLocation)
                        os.path.exists(absLocation) or os.makedirs(absLocation)
                        shutil.copy(file, absLocation)
             
    def ConfigureThirdPartyFolder(self, _thirdPartyRootFolder, _thirdPartyBinFolder):
        """ 
        Runs cmake to install the libraries in the third party folder.
        """
        os.path.exists(_thirdPartyBinFolder) or os.makedirs(_thirdPartyBinFolder)
        os.chdir(_thirdPartyBinFolder)
        print os.popen('cmake %s' % _thirdPartyRootFolder).read()
        