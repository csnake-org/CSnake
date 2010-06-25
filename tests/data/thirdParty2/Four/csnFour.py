# Csnake project configuration
import csnBuild
import csnCilab

four = csnBuild.Project("Four", "third party")
four.pathsManager.useFilePath = "%s/Four/UseFour.cmake" % four.GetBuildFolder()
four.pathsManager.configFilePath = "%s/Four/FourConfig.cmake" % four.GetBuildFolder()


