# Used to configure dummyExe
import csnBuild
import csnCilab
from csnAll import *

dummyExe = csnCilab.CilabModuleProject("DummyExe", "executable")
dummyExe.AddSources(["src/DummyExe.cpp"])
dummyExe.AddProjects([dummyLib])
