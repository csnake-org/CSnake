# Project variable definitions
from csnAPIPublic import GetAPI
api = GetAPI("2.4.5")

def dummyLib():
    import DummyLib.csnDummyLib
    return DummyLib.csnDummyLib.dummyLib
    
def cxxTest():
    return api.LoadThirdPartyModule('CxxTest', 'csnCxxTest').cxxTest

def two():
    return api.LoadThirdPartyModule('Two', 'csnTwo').two

def three():
    return api.LoadThirdPartyModule('Three', 'csnThree').three

