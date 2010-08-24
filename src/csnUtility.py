import re
import sys
import GlobDirectoryWalker
import shutil
import inspect
import os.path
if sys.platform == 'win32':
    import _winreg

def CorrectPath(path):
    (first,second) = os.path.split(path)
    
    if second != "":
        firstCorrected = CorrectPath(first)
        secondCorrected = second
        if os.path.exists(first):
            for name in os.listdir(first):
                if name.lower() == second.lower():
                    secondCorrected = name
        return os.path.join(firstCorrected, secondCorrected)
    else:
        return first

def NormalizePath(path):
    newPath = CorrectPath( os.path.normpath(path) ).replace("\\", "/")
    return newPath

def UnNormalizePath(path):
    return os.path.normpath(path).replace("/", "\\")

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
rootOfCSnake = os.path.dirname(__file__) + "/../"
rootOfCSnake = NormalizePath(rootOfCSnake)

def GetRootOfCSnake():
    return rootOfCSnake
    
def HasBackSlash(_path):
    p = re.compile(r"[^\\]*\\")
    m = p.match( _path )
    return m

def Join(_theList, _addQuotes = 0):
    """
    Returns a string that contains the items of theList separated by spaces.
    _addQuotes - If true, then each item is also placed in "quotes".
    """
    joined = ""
    
    for x in _theList:
        item = str(x)
        if _addQuotes:
            item = '"' + item + '"'
        joined = joined + item + " "
    return joined

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


def LoadModules(_folders, _name):
    """ 
    Loads python module _name from any _folders, or returns previously loaded module from the loadedModules variable (see above).
    Adds module to loadedModules (if it is not already there).
    """
    sys.path.extend(_folders)
    location = len(sys.path) - 1
    result = __import__(_name)
    #assert sys.path[location] == _folders, "\n\nError: expected that importing %s would not remove stuff from sys.path." % _name 
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
    return GetRootOfCSnake() + "/resources/csnake_dummy.cpp"

def ReplaceDestinationFileIfDifferent(sourceFile, destinationFile):
    if FileToString(sourceFile) != FileToString(destinationFile):
        result = (0 != shutil.copy(sourceFile, destinationFile))
        assert result, "\n\nError: Could not copy from %s to %s/n" % (sourceFile, destinationFile)
        
# (YM) debug output of the overwritten file to check differences
def ReplaceDestinationFileIfDifferentAndSaveBackup(sourceFile, destinationFile):
    if FileToString(sourceFile) != FileToString(destinationFile):
        if os.path.exists(destinationFile):
            result = (0 != shutil.copy(destinationFile, (destinationFile + ".old")))
            assert result, "\n\nError: Could not copy from %s to %s/n" % (destinationFile, (destinationFile + ".old"))        result = (0 != shutil.copy(sourceFile, destinationFile))
        assert result, "\n\nError: Could not copy from %s to %s/n" % (sourceFile, destinationFile)

def Matches(string, pattern):
    result = False
    wildCharPosition = pattern.find( '*' )
    if wildCharPosition == -1:
        result = pattern == string
    else:
        patternLength = len(pattern)
        if wildCharPosition == 0:
            pattern = pattern[1:] + '$'
        elif wildCharPosition == patternLength:
            pattern = '^' + pattern[:patternLength-1]
        else:
            pattern = '^' + pattern.replace( '*', "[\w]*" ) + '$'
        if re.search( pattern, string ):
            result = True
    return result

def LoadFields(parser, section, basicFields, self):
    for basicField in basicFields:
        if parser.has_option(section, basicField):
            setattr(self, basicField, parser.get(section, basicField))

def FindFilePathInStack(keyWord):
    for x in inspect.stack():
        callString = x[4][0]
        if not callString.find(keyWord) == -1:
            return NormalizePath(os.path.dirname(x[1]))
    return ""

def GetSourceFileExtensions():
    return ["cxx", "cc", "cpp"]
    
def GetIncludeFileExtensions():
    return ["h", "hpp", "txx"]

def GetDirs( startDir, outDirs, excludedFoldersList ):
    directories = [startDir]
    while len(directories)>0:
        directory = directories.pop()
        for name in os.listdir(directory):
            fullpath = os.path.join(directory,name)
            if os.path.isdir(fullpath) and not (name in excludedFoldersList):
                outDirs.append(name)  # It's a directory, store it.

def GetRegVisualStudioPath( generator, key_name ):

    if sys.platform != 'win32':
        return ""

    value = None
    type_id = None
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, key_name)
    if generator.startswith('Visual Studio 7'):
        value,type_id = _winreg.QueryValueEx(key, '7.1')
    elif generator.startswith('Visual Studio 8'):
        value,type_id = _winreg.QueryValueEx(key, '8.0')
    elif generator.startswith('Visual Studio 9'):
        value,type_id = _winreg.QueryValueEx(key, '9.0')
    elif generator.startswith('Visual Studio 10'):
        value,type_id = _winreg.QueryValueEx(key, '10.0')
    else:
        raise Exception('Cannot find Visual Studio location for: ' + generator)
    path = value + r'Common7\IDE\devenv.exe'
    if not os.path.exists(path):
        raise Exception("'%s' not found." % path)
    return path

def GetDefaultVisualStudioPath( generator ):
    try:
        path = GetRegVisualStudioPath( generator, r'SOFTWARE\Wow6432Node\Microsoft\VisualStudio\SxS\VS7' )
    except WindowsError:
        path = GetRegVisualStudioPath( generator, r'SOFTWARE\Microsoft\VisualStudio\SxS\VC7' )
    return path

