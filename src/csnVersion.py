## @package csnVersion
# Class to parse, compare and show version numbers of CSnake.
import exceptions
import re

class Version:
    versionModifierValue = { "alpha"  : -10000,
                             "alpha1" : -15000,
                             "alpha2" : -14999,
                             "alpha3" : -14998,
                             "alpha4" : -14997,
                             "alpha5" : -14996,
                             "beta"   : -10000,
                             "beta1"  : -10000,
                             "beta2"  : -9999,
                             "beta3"  : -9998,
                             "beta4"  : -9997,
                             "beta5"  : -9996,
                             "rc1"    : -5000,
                             "rc2"    : -4999,
                             "rc3"    : -4998,
                             "rc4"    : -4997,
                             "rc5"    : -4996,
                             ""       : 0,
                             None     : 0 }
    
    __hash__ = None
    
    def __init__(self, version):
        """ Input version is either 
            - a string (ex:"1.22.3"),
            - an array of strings (ex:["1", "22", "3"]).
            - an array of ints (ex:[1, 22, 3]). """
        if isinstance(version, str):
            self.__GetVersionFromString(version)
        elif isinstance(version, list):
            self.__GetVersionFromArray(version)
        else:
            raise AssertionError("The input version is neither a string or an array.")
        assert self.__versionModifier in Version.versionModifierValue
        
    def __GetVersionFromArray(self, versionArray):
        # Check for version modifier
        self.__versionModifier = ""
        if isinstance(versionArray[-1], str): # is it a string
            try:
                int(versionArray[-1])
            except ValueError: # is the string a real non-number-string (and not just a number in a string)
                self.__versionModifier = versionArray[-1]
                versionArray = versionArray[:-1]
        
        # convert numeric part of the array in ints (might be an array of string that represent numbers)
        assert versionArray
        self.__versionNumber = map(int, versionArray)
        
        # normalize it
        while len(self.__versionNumber) > 0 and self.__versionNumber[-1] == 0:
            self.__versionNumber.pop()
    
    def __GetVersionFromString(self, versionString):
        # divide "1.2.3beta", "1.2.3.beta", "1.2.3 beta" etc. in "1.2.3" and "beta"
        m = re.match('([0-9]+(\\.[0-9]+)*)[^a-zA-Z0-9]*(.*)', versionString)
        pureVersionString = m.group(1)
        self.__versionModifier = m.group(3) # alpha, beta, rc1, etc.
        
        # convert version string into an array of ints
        self.__versionNumber = map(int, pureVersionString.split('.'))
        
        # normalize it
        while len(self.__versionNumber) > 0 and self.__versionNumber[-1] == 0:
            self.__versionNumber.pop()
    
    def GetString(self, numDecimals = 2):
        zeroes = [0 for i in range(0, numDecimals + 1 - len(self.__versionNumber))]
        return "%s-%s" % (".".join(map(str, self.__versionNumber + zeroes)), self.__versionModifier)
    
    def __cmp__(self, other):
        commonLength = min(len(self.__versionNumber), len(other.__versionNumber))
        for i in range(0, commonLength):
            if self.__versionNumber[i] != other.__versionNumber[i]:
                return self.__versionNumber[i] - other.__versionNumber[i]
        if len(self.__versionNumber) == len(other.__versionNumber):
            return Version.versionModifierValue[self.__versionModifier] - Version.versionModifierValue[other.__versionModifier]
        elif len(self.__versionNumber) > len(other.__versionNumber):
            return 1
        else:
            return -1

