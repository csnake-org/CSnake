import csnBuild
myLibrary = csnBuild.Project("MyLibrary", "library")
myLibrary.AddSources(["src/MyLibrary.cpp", "src/MyLibrary.h"])
myLibrary.AddIncludeFolders(["src"])