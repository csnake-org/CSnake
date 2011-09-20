# Used to configure CxxTest
from csnAPIPublic import GetAPI
api = GetAPI("2.4.5")

cxxTest = api.CreateCompiledProject("CxxTest", "library")
