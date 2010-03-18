# Used to configure dummyLib
import csnCilab

dummyLib = csnCilab.CilabModuleProject("DummyLib", "library")
dummyLib.AddLibraryModules(["dummyLib"])
dummyLib.AddApplications(["myApp"])