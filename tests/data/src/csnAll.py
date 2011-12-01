# Project variable definitions
import csnCilab
import csnBuild

def dummyLib():
    import DummyLib.csnDummyLib
    return DummyLib.csnDummyLib.dummyLib
    
def cxxTest():
    return csnCilab.LoadThirdPartyModule('CxxTest', 'csnCxxTest').cxxTest

def two():
    return csnCilab.LoadThirdPartyModule('Two', 'csnTwo').two

def three():
    return csnCilab.LoadThirdPartyModule('Three', 'csnThree').three

def four():
    return csnCilab.LoadThirdPartyModule('Four', 'csnFour').four

# Toolkit header -------------------------------------------------------------------------
toolkit = csnBuild.Project("TestToolkit", "library")
toolkit.AddCustomCommand( csnCilab.CreateToolkitHeader )
