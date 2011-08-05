## @package csnAPIPublic
# API for the communication between csnake files and csnake

# This is the only CSnake module that should be imported by CSnake files.

import csnAPIImplementation

def GetAPIByVersion(_versionArray = None, _versionString = None):
    if _versionString is None:
        if _versionArray is None:
            raise csnAPIImplementation.APIError("You have to give a version number!")
        else:
            versionArray = None # TODO: split string
    else:
        if _versionArray is None:
            versionArray = _versionArray
        else:
            raise csnAPIImplementation.APIError("Please, give the version number in only one format!")
    return csnAPIImplementation.FindAPI(_versionArray)

