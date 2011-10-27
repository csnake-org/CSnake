# Used to configure CxxTest
from csnAPIPublic import GetAPI
api = GetAPI("2.5.0-beta")

cxxTest = api.CreateCompiledProject("CxxTest", "library")
