# Csnake project configuration
from csnAPIPublic import GetAPI
api = GetAPI("2.4.5")
from csnAll import three

four = api.CreateThirdPartyProject("Four")
four.SetUseFilePath("%s/Four/UseFour.cmake" % four.GetBuildFolder())
four.SetConfigFilePath("%s/Four/FourConfig.cmake" % four.GetBuildFolder())
four.AddProjects([three])

