import os.path
import re
import imp

def Log(logString):
        f = open("c:\\log.txt", 'a')
        f.write(logString)
        f.close()

def HasBackSlash(_path):
    p = re.compile(r"[^\\]*\\")
    m = p.match( _path )
    return m

def Join(theList):
    """
    Returns a string that contains the items of theList separated by spaces.
    """
    all = ""
    for x in theList:
        all = all + str(x) + " "
    return all

def LoadModule(_folder, _name):
    """ Loads python module _name from _folder """
    found = imp.find_module(_name, [_folder])
    
    result = None
    if found:
        (file, pathname, description) = found
        try:
            result = imp.load_module(_name, file, pathname, description)
        finally:
            file.close()
    return result

def FileToString(_filename):
    x = ""
    if( os.path.exists(_filename) ):
        f = open(_filename, 'r')
        x = f.read()
        f.close()
    return x
