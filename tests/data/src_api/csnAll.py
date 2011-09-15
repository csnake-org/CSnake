# Project variable definitions
import csnCilab

def dummyLib():
    import DummyLib.csnDummyLib
    return DummyLib.csnDummyLib.dummyLib
    
def cxxTest():
    return csnCilab.LoadThirdPartyModule('CxxTest', 'csnCxxTest').cxxTest

def two():
    return csnCilab.LoadThirdPartyModule('Two', 'csnTwo').two

def three():
    return csnCilab.LoadThirdPartyModule('Three', 'csnThree').three

