import csnBuild
from csnCISTIBToolkit import *

myLibrary = csnBuild.Project("MyLibrary", "library")
myLibrary.AddSources(["src/myLibrary.cpp", "src/myLibrary.h"])
myLibrary.AddIncludeFolders(["src"])
myLibrary.AddTests(["test/*.h"], cxxTest)
