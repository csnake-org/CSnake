# Csnake project configuration
import csnCilab

four = csnCilab.CilabModuleProject("Four", "third party")
four.pathsManager.useFilePath = "%s/Four/UseFour.cmake" % four.GetBuildFolder()
four.pathsManager.configFilePath = "%s/Four/FourConfig.cmake" % four.GetBuildFolder()


