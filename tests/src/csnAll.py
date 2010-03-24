# Project variable definitions
import csnCilab

def dummyLib():
    import DummyLib.csnDummyLib
    return DummyLib.csnDummyLib.dummyLib
    
def cxxTest():
    return csnCilab.LoadThirdPartyModule('CxxTest', 'csnCxxTest').cxxTest

