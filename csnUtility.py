import os
import re
import imp
import sys
import GlobDirectoryWalker
import shutil

def NormalizePath(path):
    return os.path.normpath(path).replace("\\", "/")

def RemovePrefixFromPath(path, prefix):
    prefix = os.path.commonprefix([NormalizePath(path), NormalizePath(prefix)] )
    return path[len(prefix):]

def CopyFolder(fromFolder, toFolder, excludedFolderList = None):
    if excludedFolderList is None:
        excludedFolderList = []
    
    for file in GlobDirectoryWalker.Walker(fromFolder, ["*"], excludedFolderList):
        target = NormalizePath(toFolder + "/" + RemovePrefixFromPath(file, fromFolder))
        if os.path.isdir(file):
            if not os.path.exists(target):
                #print "makedirs %s\n" % newFolder
                os.makedirs(target)
        else:
            targetFolder = os.path.dirname(target)
            if not os.path.exists(targetFolder):
                #print "mkdirs %s\n" % targetFolder
                os.makedirs(targetFolder)
            #print "Copy %s to %s\n" % (file, target)
            shutil.copy(file, target)
            
def IsRunningOnWindows():
    """ Returns true if the python script is not running on Windows """
    return sys.platform == "win32"

# create variable that contains the folder where csnake is located. The use of /../CSnake ensures that 
# the root folder is set correctly both when running the python interpreter, or when using the binary
# CSnakeGUI executable.
rootOfCSnake = os.path.dirname(__file__) + "/../CSnake"
rootOfCSnake = NormalizePath(rootOfCSnake)

def GetRootOfCSnake():
    return rootOfCSnake
    
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

def LoadModule(_folder, _name):
    """ 
    Loads python module _name from _folder, or returns previously loaded module from the loadedModules variable (see above).
    Adds module to loadedModules (if it is not already there).
    """
    sys.path.append(_folder)
    location = len(sys.path) - 1
    result = __import__(_name)
    assert sys.path[location] == _folder, "\n\nError: expected that importing %s would not remove stuff from sys.path." % _name 
    sys.path.pop(location)
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
    return GetRootOfCSnake() + "/TemplateSourceFiles/csnake_dummy.cpp"

def ReplaceDestinationFileIfDifferent(sourceFile, destinationFile):
    if FileToString(sourceFile) != FileToString(destinationFile):
        result = (0 != shutil.copy(sourceFile, destinationFile))
        assert result, "\n\nError: Could not copy from %s to %s/n" % (sourceFile, destinationFile)
