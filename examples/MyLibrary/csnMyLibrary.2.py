import csnBuild
import csnUtility

myDll = csnBuild.Project("MyDll", "dll")
myDll.AddSources([csnUtility.GetDummyCppFilename()])

myLibrary = csnBuild.Project("MyLibrary", "library")
myLibrary.AddSources(["src/MyLibrary.cpp", "src/MyLibrary.h"])
myLibrary.AddIncludeFolders(["src"])
myLibrary.AddProjects([myDll])
