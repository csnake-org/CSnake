import os
import sys
import csnUtility
import csnBuild

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
        
    def ConfigureProjectToBinFolder(self, _projectPath, _instance, _sourceRootFolder, _binFolder, _thirdPartyRootFolder, _thirdPartyBinFolder, _alsoRunCMake):
        (projectFolder, name) = os.path.split(_projectPath)
        (name, ext) = os.path.splitext(name)
        binFolder = _binFolder.replace("\\", "/")
        
        # extend python path with project folder, source root and third party root
        addedToPythonPath = set()
        for path in (_projectPath, _sourceRootFolder, _thirdPartyRootFolder):
            if not path in sys.path:
                sys.path.append(path)
                addedToPythonPath.add(path)
    
        csnUtility.UnloadAllModules()
        project = csnUtility.LoadModule(projectFolder, name)   
        exec "instance = project.%s" % _instance
        generator = csnBuild.Generator()
        generator.Generate(instance, binFolder)
    
        # undo additions to the python path
        for path in addedToPythonPath:
            sys.path.remove(path)
            
        if _alsoRunCMake:
            fileCMakeLists = "%s/%s" % (binFolder, instance.cmakeListsSubpath)
            os.system('cmake %s' % os.path.dirname(fileCMakeLists))
