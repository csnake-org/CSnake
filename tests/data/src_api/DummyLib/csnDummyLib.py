# Used to configure dummyLib
import csnBuild
import csnCilab
from csnAll import *

# define project
dummyLib = csnCilab.CilabModuleProject("DummyLib", "library")
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