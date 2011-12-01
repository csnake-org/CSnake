# Used to configure dummyLib
import csnBuild
import csnCilab
from csnAll import *
import os.path

# define project
dummyLib = csnCilab.CilabModuleProject("DummyLib", "library")
# dependencies
# (four depends on three that should be also added implicitly)
dummyLib.AddProjects([two, four, toolkit])
# source folders
dummyLib.AddLibraryModules(["dummyLib"])
# applications
dummyLib.AddApplications(["myApp"])
# tests
dummyLib.AddTests(["tests/DummyTest/*.h"], cxxTest)
# creates a dependency on thirdParty/cmakeMacros/PCHSupport_26.cmake
found = dummyLib.Glob("*PCH.h")
pchFile = os.path.basename(found[0])
dummyLib.SetPrecompiledHeader(pchFile)
# add compiler definitions
dummyLib.AddDefinitions(["-Wall -Werror"], _private = 1, _WIN32 = 0, _NOT_WIN32 = 1)
dummyLib.AddDefinitions(["-W4 -WX"], _private = 1, _WIN32 = 1, _NOT_WIN32 = 0)
# search for some files
