## @package csnBuild
# Prevent warnings.
from csnProject import Project, globalCurrentContext
from csnGenerator import Generator, version, ToProject

def PreventWarnings():
    Project
    globalCurrentContext
    Generator
    version
    ToProject
    