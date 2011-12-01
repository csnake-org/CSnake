# Used to configure dummyLib
from csnAll import *
from csnAPIPublic import GetAPI
import os.path
api = GetAPI("2.5.0-beta")

# define project
dummyLib = api.CreateStandardModuleProject("DummyLib", "library")
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
if api.GetCompiler().TargetIsWindows():
    dummyLib.AddDefinitions(["-W4 -WX"], private = 1)
else:
    dummyLib.AddDefinitions(["-Wall -Werror"], private = 1)
