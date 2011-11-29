# Used to configure dummyLib2
import csnBuild
import csnCilab
from csnAll2 import *

# define project
dummyLib2 = csnCilab.CilabModuleProject("DummyLib2", "library")
# dependencies
dummyLib2.AddProjects([two, four, five])
# source folders
dummyLib2.AddLibraryModules(["dummyLib2"])
# applications
dummyLib2.AddApplications(["myApp"])
# tests
dummyLib2.AddTests(["tests/DummyTest/*.h"], cxxTest)
# creates a dependency on thirdParty/cmakeMacros/PCHSupport_26.cmake
dummyLib2.SetPrecompiledHeader("dummyLib2PCH.h")