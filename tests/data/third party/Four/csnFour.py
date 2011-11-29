# Csnake project configuration
import csnCilab
from csnAll import three

four = csnCilab.CilabModuleProject("Four", "third party")
four.pathsManager.useFilePath = "%s/Four/UseFour.cmake" % four.GetBuildFolder()
four.pathsManager.configFilePath = "%s/Four/FourConfig.cmake" % four.GetBuildFolder()
four.AddProjects([three])

