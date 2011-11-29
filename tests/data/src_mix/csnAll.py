# Project variable definitions
from csnAPIPublic import GetAPI
api = GetAPI("2.5.0-beta")

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

