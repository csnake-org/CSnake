import csnBuild
import csnCISTIBToolkit

myLibrary = csnBuild.Project("MyLibrary", "library")
myLibrary.AddSources(["src/MyLibrary.cpp", "src/MyLibrary.h"])
myLibrary.AddIncludeFolders(["src"])

itk = csnCISTIBToolkit.itk()
myLibrary.AddProjects([itk])
