import os
from csnGUIHandler import NotARoot, RootNotFound

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
