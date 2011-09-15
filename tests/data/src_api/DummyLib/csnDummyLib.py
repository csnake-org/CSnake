# Used to configure dummyLib
from csnAll import *
from csnAPIPublic import GetAPI
api = GetAPI("2.4.5")

# define project
dummyLib = api.CreateStandardModuleProject("DummyLib", "library")
# dependencies
dummyLib.AddProjects([two, three])
# source folders
dummyLib.AddLibraryModules(["dummyLib"])
# applications
dummyLib.AddApplications(["myApp"])
# tests
dummyLib.AddTests(["tests/DummyTest/*.h"], cxxTest)
# creates a dependency on thirdParty/cmakeMacros/PCHSupport_26.cmake
dummyLib.SetPrecompiledHeader("dummyLibPCH.h")