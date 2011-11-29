# Used to configure dummyExe
from csnAll import *
from csnAPIPublic import GetAPI
api = GetAPI("2.5.0-beta")

dummyExe = api.CreateStandardModuleProject("DummyExe", "executable")
dummyExe.AddSources(["src/DummyExe.cpp"])
dummyExe.AddProjects([dummyLib])
