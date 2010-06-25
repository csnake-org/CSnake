# Csnake project configuration
import csnBuild
import csnCilab

three = csnBuild.Project("Three", "third party")
three.pathsManager.useFilePath = "%s/Three/UseThree.cmake" % three.GetBuildFolder()
three.pathsManager.configFilePath = "%s/Three/ThreeConfig.cmake" % three.GetBuildFolder()


