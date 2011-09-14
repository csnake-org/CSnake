## @package csnAPIPublic
# API for the communication between csnake files and csnake

# This is the only CSnake module that should be imported by CSnake files.

import csnAPIImplementation

def GetAPI(version):
    """ Get the API corresponding to the input Version object. """
    return csnAPIImplementation.FindAPI(version)
