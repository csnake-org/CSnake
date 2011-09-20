# Csnake project configuration
from csnAPIPublic import GetAPI
api = GetAPI("2.4.5")

three = api.CreateThirdPartyProject("Three")
three.SetUseFilePath( "%s/Three/UseThree.cmake" % three.GetBuildFolder() )
three.SetConfigFilePath( "%s/Three/ThreeConfig.cmake" % three.GetBuildFolder() )


