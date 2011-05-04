# Csnake project configuration
import csnCilab

three = csnCilab.CilabModuleProject("Three", "third party")
three.pathsManager.useFilePath = "%s/Three/UseThree.cmake" % three.GetBuildFolder()
three.pathsManager.configFilePath = "%s/Three/ThreeConfig.cmake" % three.GetBuildFolder()


