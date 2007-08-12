import gbBuild

class Itk (gbBuild.Project):
	def __init__(self):
		self.Init("Itk", "library")
		self.publicIncludePaths = ["ItkIncludePath"]
		self.publicLibraryPaths = ["ItkLibraryPath"]

itk = Itk()

