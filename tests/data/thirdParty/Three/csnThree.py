# Csnake project configuration
import csnCilab
from csnAll import four

three = csnCilab.CilabModuleProject("Three", "third party")
three.pathsManager.useFilePath = "%s/Three/UseThree.cmake" % three.GetBuildFolder()
three.pathsManager.configFilePath = "%s/Three/ThreeConfig.cmake" % three.GetBuildFolder()
three.UseBefore(four)

