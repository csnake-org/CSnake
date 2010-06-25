# Csnake project configuration
import csnBuild
import csnCilab

two = csnBuild.Project("Two", "third party")
two.pathsManager.useFilePath = "%s/Two/UseTwo.cmake" % two.GetBuildFolder()
two.pathsManager.configFilePath = "%s/Two/TwoConfig.cmake" % two.GetBuildFolder()

two.AddFilesToInstall(["bin\Debug\TwoLib.dll"], _debugOnly = 1, _WIN32 = 1)
two.AddFilesToInstall(["bin\Release\TwoLib.dll"], _releaseOnly = 1, _WIN32 = 1)

