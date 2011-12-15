# Project variable definitions
from csnAPIPublic import GetAPI
api = GetAPI("2.5.0")

def dummyLib():
    import DummyLib.csnDummyLib
    return DummyLib.csnDummyLib.dummyLib
    
def cxxTest():
    return api.LoadThirdPartyModule('CxxTest', 'csnCxxTest').cxxTest

def two():
    return api.LoadThirdPartyModule('Two', 'csnTwo').two

def three():
    return api.LoadThirdPartyModule('Three', 'csnThree').three

def four():
    return api.LoadThirdPartyModule('Four', 'csnFour').four

# Toolkit header -----------------------------------
toolkit = api.CreateCompiledProject("TestToolkit", "library")
headerVariables = { "ANSWER_TO_LIFE_THE_UNIVERSE_AND_EVERYTHING" : "42" }
toolkit.CreateHeader("ToolkitHeader.h", headerVariables, "TESTTK")
