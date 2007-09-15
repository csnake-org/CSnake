import csnBuild

itk = csnBuild.Project("Itk", "library")
itk.publicIncludePaths = ["ItkIncludePath"]
itk.publicLibraryPaths = ["ItkLibraryPath"]
itk.publicLibraries = ["Itk"]
itk.includeBeforeThese = ["Mitk"]

mitk = csnBuild.Project("Mitk", "library")
mitk.publicIncludePaths = ["MitkIncludePath"]
mitk.publicLibraryPaths = ["MitkLibraryPath"]
mitk.publicLibraries = ["Mitk"]
mitk.AddProject(itk)


