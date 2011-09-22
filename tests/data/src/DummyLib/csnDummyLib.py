# Used to configure dummyLib
import csnBuild
import csnCilab
from csnAll import *

# define project
dummyLib = csnCilab.CilabModuleProject("DummyLib", "library")
# dependencies
# (four depends on three that should be also added implicitly)
dummyLib.AddProjects([two, four])
# source folders
dummyLib.AddLibraryModules(["dummyLib"])
# applications
dummyLib.AddApplications(["myApp"])
# tests
dummyLib.AddTests(["tests/DummyTest/*.h"], cxxTest)
# creates a dependency on thirdParty/cmakeMacros/PCHSupport_26.cmake
dummyLib.SetPrecompiledHeader("dummyLibPCH.h")
# add compiler definitions
dummyLib.AddDefinitions(["-Wall -Werror"], _private = 1, _WIN32 = 1, _NOT_WIN32 = 1)
