# Used to configure dummyExe
from csnAll import *
from csnAPIPublic import GetAPI
api = GetAPI("2.4.5")

dummyExe = api.CreateStandardModuleProject("DummyExe", "executable")
dummyExe.AddSources(["src/DummyExe.cpp"])
dummyExe.AddProjects([dummyLib])
