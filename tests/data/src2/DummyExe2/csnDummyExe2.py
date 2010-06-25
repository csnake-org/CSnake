# Used to configure dummyExe
import csnCilab
from csnAll import *

dummyExe2 = csnCilab.CilabModuleProject("DummyExe2", "executable")
dummyExe2.AddSources(["src/DummyExe2.cpp"])
dummyExe2.AddProjects([dummyLib])
