# Csnake project configuration
import csnCilab

five = csnCilab.CilabModuleProject("Five", "third party")
five.pathsManager.useFilePath = "%s/Five/UseFive.cmake" % five.GetBuildFolder()
five.pathsManager.configFilePath = "%s/Five/FiveConfig.cmake" % five.GetBuildFolder()


