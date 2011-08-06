## @package csnBuild
# Prevent warnings.
from csnProject import Project, globalCurrentContext
from csnGenerator import Generator, version, versionObject, versionString, ToProject

def PreventWarnings():
    Project
    globalCurrentContext
    Generator
    version         # still there for compatibility and has the same value as versionString
    versionObject
    versionString
    ToProject
    
