# Used to configure dummyLib
import csnCilab
from csnAll import *

dummyLib = csnCilab.CilabModuleProject("DummyLib", "library")
dummyLib.AddLibraryModules(["dummyLib"])
dummyLib.AddApplications(["myApp"])
dummyLib.AddTests(["tests/dummyTest/*.h"], cxxTest)
