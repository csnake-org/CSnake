import csnBuild

myLibrary = csnBuild.Project("MyLibrary", "library")
myLibrary.AddSources(["src/myLibrary.cpp", "src/myLibrary.h"])
myLibrary.AddIncludeFolders(["src"])

if __name__ == "__main__":
    generator = csnBuild.Generator()
    generator.Generate(myLibrary, "./bin", "./install")