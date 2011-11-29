# Used to configure dummyLib
import csnBuild
import csnCilab
from csnAll import *

dummyLib = csnCilab.CilabModuleProject("DummyLib", "library")
dummyLib.AddLibraryModules(["dummyLib"])
dummyLib.AddApplications(["myApp"])
dummyLib.AddTests(["tests/DummyTest/*.h"], cxxTest)
# creates a dependency on thirdParty/cmakeMacros/PCHSupport_26.cmake
dummyLib.SetPrecompiledHeader("dummyLibPCH.h")