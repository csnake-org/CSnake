# Csnake project configuration
from csnAPIPublic import GetAPI
api = GetAPI("2.5.0-beta")

two = api.CreateThirdPartyProject("Two")
two.SetUseFilePath( "%s/Two/UseTwo.cmake" % two.GetBuildFolder() )
two.SetConfigFilePath( "%s/Two/TwoConfig.cmake" % two.GetBuildFolder() )

two.AddFilesToInstall(["bin\Debug\TwoLib.dll"], debugOnly = 1, WIN32 = 1)
two.AddFilesToInstall(["bin\Release\TwoLib.dll"], releaseOnly = 1, WIN32 = 1)

