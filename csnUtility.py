import os.path
import re
import imp
import csnBuild
import csnUtility
import sys

def Log(logString):
        f = open("F:\\log.txt", 'a')
        f.write(logString)
        f.close()

def HasBackSlash(_path):
    p = re.compile(r"[^\\]*\\")
    m = p.match( _path )
    return m

def Join(_theList, _addQuotes = 0):
    """
    Returns a string that contains the items of theList separated by spaces.
    _addQuotes - If true, then each item is also placed in "quotes".
    """
    all = ""
    
    for x in _theList:
        item = str(x)
        if _addQuotes:
            item = '"' + item + '"'
        all = all + item + " "
    return all

# used by LoadModule
loadedModules = dict()

def LoadModule(_folder, _name):
    """ 
    Loads python module _name from _folder, or returns previously loaded module from the loadedModules variable (see above).
    Adds module to loadedModules (if it is not already there).
    """
    key = os.path.normpath(_folder) + "_WITH_NAME_" + _name
    result = None
    if loadedModules.has_key(key):
        result = loadedModules[key]
    else:
        print "LoadModule %s in %s" % (_name, _folder)
        found = imp.find_module(_name, [_folder])
        if found:
            (file, pathname, description) = found
            try:
                result = imp.load_module(_name, file, pathname, description)
                loadedModules[key] = result
            finally:
                file.close()
        print "...Finished LoadModule %s in %s" % (_name, _folder)
    return result

def FileToString(_filename):
    x = ""
    if( os.path.exists(_filename) ):
        f = open(_filename, 'r')
        x = f.read()
        f.close()
    return x

def GetDummyCppFilename():
    """ 
    Returns name of the file that can be used in any project to prevent the project from having zero source files. 
    This is needed when you call ADD_DEPENDENCY (CMake complains if you use a project there that does not have sources).
    """
    return csnBuild.root + "/CSnake/TemplateSourceFiles/csnake_dummy.cpp"
