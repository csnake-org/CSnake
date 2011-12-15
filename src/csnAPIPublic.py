## @package csnAPIPublic
# API for the communication between csnake files and csnake
# \ingroup api

# This is the only CSnake module that should be imported by CSnake files.

import csnAPIImplementation

def GetAPI(version):
    """ Get the API corresponding to the input version. 
    Version can be either 
        - a string (ex:"1.22.3"),
        - an array of strings (ex:["1", "22", "3"]).
        - an array of ints (ex:[1, 22, 3]). """
    return csnAPIImplementation.FindAPI(version)
