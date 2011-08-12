## @package csnUtility
# Definition of utility methods. 
import re
import sys
import GlobDirectoryWalker
import shutil
import inspect
import os.path
import logging.config
if sys.platform == 'win32':
    import _winreg
if sys.platform != 'win32':
    import commands

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

def NormalizePath(path, _correctCase = True):
    path = os.path.normpath(path)
    if _correctCase:
        path = CorrectPath(path)
    path = path.replace("\\", "/")
    return path

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
                os.makedirs(target)
        else:
            targetFolder = os.path.dirname(target)
            if not os.path.exists(targetFolder):
                os.makedirs(targetFolder)
            shutil.copy(file, target)
            
def IsWindowsPlatform():
    """ Returns true if the python script is running on Windows. """
    return sys.platform == "win32" or sys.platform == "cygwin"

def IsMacPlatform():
    """ Returns true if the python script is running on Mac. """
    return sys.platform == "darwin"

def IsLinuxPlatform():
    """ Returns true if the python script is running on Unix or Unix like. """
    return sys.platform == "linux2"

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
            assert result, "\n\nError: Could not copy from %s to %s/n" % (destinationFile, (destinationFile + ".old"))
        result = (0 != shutil.copy(sourceFile, destinationFile))
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

def GetDefaultVisualStudioPath( generator ):
    path = None
    key_names = [
        r'SOFTWARE\Wow6432Node\Microsoft\VisualStudio\SxS\VS7', # typical windows XP
        r'SOFTWARE\Microsoft\VisualStudio\SxS\VS7'] #typical windows vista, 7
    value_names = []
    if generator.startswith('Visual Studio 7'): #2003
        value_names = [r"7.1"]
    elif generator.startswith('Visual Studio 8'): #2005
        value_names = [r"8.0"]
    elif generator.startswith('Visual Studio 9'): #2008
        value_names = [r"9.0"]
    elif generator.startswith('Visual Studio 10'): #2010
        value_names = [r"10.0"]
    path_end = r"Common7\IDE\devenv.exe"
    try:
        path = SearchWindowsProgramPath( key_names, value_names, path_end )
    except OSError:
        path = None
        
    return path

def GetDefaultCMakePath():
    """ Get the path to CMake. """
    path = None
    if IsWindowsPlatform():
        versions = [ r"2.8.5", r"2.8.4", r"2.8.3", r"2.8.2", r"2.8.1", r"2.8.0" ]
        key_names = []
        for version in versions:
            key_names.append(r"SOFTWARE\Wow6432Node\Kitware\CMake %s" % version) # typical windows XP
            key_names.append(r"SOFTWARE\Kitware\CMake %s" % version) #typical windows vista, 7
        value_names = [r""]
        path_end = r"\bin\cmake.exe"
        try:
            path = SearchWindowsProgramPath( key_names, value_names, path_end )
        except OSError:
            path = None
    elif IsLinuxPlatform() or IsMacPlatform():
        try:
            path = SearchUnixProgramPath("cmake")
        except OSError:
            path = None
        
    return path

def GetDefaultPythonPath():
    """ Get the path to Python. """
    path = None
    if IsWindowsPlatform():
        versions = [ r"2.7", r"2.6" ]
        key_names = []
        for version in versions:
            key_names.append(r"SOFTWARE\Wow6432Node\Python\PythonCore\%s\InstallPath" % version) # typical windows XP
            key_names.append(r"SOFTWARE\Python\PythonCore\%s\InstallPath" % version) #typical windows vista, 7
        value_names = [r""]
        path_end = r"python.exe"
        try:
            path = SearchWindowsProgramPath( key_names, value_names, path_end )
        except OSError:
            path = None
    elif IsLinuxPlatform() or IsMacPlatform():
        try:
            path = SearchUnixProgramPath("python")
        except OSError:
            path = None
        
    return path

def SearchWindowsProgramPath(key_names, value_names, path_end):
    """ 
    Search a program path on a Windows machine using the registry.
    \param path_end Unicode string to append at the end of the registry value.
    \param key_names List of registry keys to try. Will stop at the first valid one.
    \param value_names List of registry values. Will stop at the first valid one.
    \return An existing path or raises OSError if nothing found.
    """
    # logging init
    logger = logging.getLogger("CSnake")
    logger.debug( "Windows search for '%s'." % path_end )
    for key_name in key_names:
        try:
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, key_name)
        except OSError:
            logger.debug( "Key '%s' does not exist." % key_name)
            # If not found, try the next key_name
            continue
        for value_name in value_names:
            try:
                (value, type_id) = _winreg.QueryValueEx(key, value_name)
            except OSError:
                logger.debug( "Value '%s' does not exist." % value_name)
                # If not found, try the next value_name
                continue
            path = "%s%s" % (value, path_end)
            if os.path.exists(path):
                logger.debug( "Found '%s'." % path )
                return path
            else:
                logger.debug( "Incorrect path '%s'." % path )
    # If here, no value was found
    message = "Could not find a default path for '%s'." % path_end
    raise OSError(message)

def SearchUnixProgramPath(name):
    """ 
    Search a program path on a Unix machine using the 'which' command.
    \param name The name of the program.
    \return An existing path or raises OSError if nothing found.
    """
    # logging init
    logger = logging.getLogger("CSnake")
    logger.debug( "Unix search for '%s'." % name )
    # Using 'which'
    (status, path) = commands.getstatusoutput('which %s' % name)
    if status == 0 and os.path.exists(path):
        return path
    # If here, no value was found
    message = "Could not find a default path for '%s'." % name
    raise OSError(message)

def GetCSnakeUserFolder():
    """ Get the csnake folder. """
    # csnake user folder
    userFolder = os.path.expanduser("~") + "/.csnake"
    # create it if it does not exist
    if not os.path.exists(userFolder):
        os.mkdir(userFolder)
    return userFolder

def InitialiseLogging():
    # get the user folder
    userFolder = GetCSnakeUserFolder()
    # log file name
    logfilename = userFolder + "/log.txt"
    # set an environment variable to retrieve it in the log configuration
    os.environ["CSNAKELOGFILE"] = logfilename
    # logging initialization (should create the log file)
    logging.config.fileConfig(GetRootOfCSnake() + "/resources/logging.conf")
    
