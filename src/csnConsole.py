## @package csnConsole
# Command line interface for CSnake. 
import csnGUIHandler
import sys
from optparse import OptionParser
import os.path

class AskUser:
    def __init__(self):
        self.__questionYesNo = 1
        self.__answerYes = 1
        self.__answerNo = 1
        
        self.__questionType = self.__questionYesNo
    
    def QuestionYesNo(self):
        return self.__questionYesNo
    
    def AnswerYes(self):
        return self.__answerYes
    
    def AnswerNo(self):
        return self.__answerNo
    
    def SetType(self, questionType):
        self.__questionType = questionType
    
    def Ask(self, message, defaultAnswer):
        if self.__questionType == self.__questionYesNo:
            message = "%s (yes/no) > " % message
            answer = ""
            answerDictionary = { "yes" : self.__answerYes, "y" : self.answerYes, "no" : self.__answerNo, "n" : self.__answerNo }
            while not answer in answerDictionary:
                answer = input(message).lower()
            return answerDictionary[answer]
        else:
            raise Exception("Invalid question type!")

class DontAskUser:
    def QuestionYesNo(self):
        return 1
    
    def AnswerYes(self):
        return 1
    
    def AnswerNo(self):
        return 2
    
    def SetType(self, questionType):
        pass
    
    def Ask(self, message, defaultAnswer):
        if self.__questionType == self.QuestionYesNo():
            if defaultAnswer == self.AnswerYes():
                answer = "yes"
            elif defaultAnswer == self.AnswerNo():
                answer = "no"
            else:
                raise Exception("Invalid defaultAnswer!")
        else:
            raise Exception("Invalid question type!")
        print "A project wants to ask you the following question:\n"
        print message
        print "\nAs you have let us know that you don't want to be bothered, we decide for you. The answer is: \"%s\"" % answer

parser = OptionParser(usage="%prog contextFile [options]")
parser.add_option("-i", "--install", dest="install", action="store_true", default=False, help="install files to build folder")
parser.add_option("-t", "--thirdParty", dest="thirdParty", action="store_true", default=False, help="configure third party projects")
parser.add_option("-p", "--project", dest="project", action="store_true", default=False, help="configure project")
parser.add_option("-c", "--configure", action="store_true", default=False, help="configure all")
parser.add_option("-b", "--build", action="store_true", default=False, help="build all")
parser.add_option("-a", "--autoconfig", dest="autoconfig", action="store_true", default=False, help="configure third party or project depending on the context instance")
parser.add_option("-s", "--silent", dest="silent", action="store_true", default=False, help="Don't ask any questions.")
(commandLineOptions, commandLineArgs) = parser.parse_args()


# check command line
if len(commandLineArgs) != 1:
    parser.print_usage()
    sys.exit(1)

# check if the file exists
if not os.path.exists(commandLineArgs[0]):
    print "Error, the input context file does not exists: '%s'" % commandLineArgs[0]
    sys.exit(1)

handler = csnGUIHandler.Handler()
context = handler.LoadContext(commandLineArgs[0])

if commandLineOptions.silent:
    askUser = DontAskUser()
else:
    askUser = AskUser()

# configure third parties and project (used by Gimias)
if commandLineOptions.configure:
    result = handler.ConfigureThirdPartyFolders()
    assert result, "\n\n[CSnake] Task failed: ConfigureThirdPartyFolders." 
    print "\n\n[CSnake] Task finished successfully: ConfigureThirdPartyFolders.\n"
    result = handler.ConfigureProjectToBuildFolder(_alsoRunCMake = True, _askUser = askUser)
    assert result, "\n\n[CSnake] Task failed: ConfigureProjectToBuildFolder." 
    print "\n\n[CSnake] Task finished successfully: ConfigureProjectToBuildFolder.\n"

# build third parties and project + install files (used by Gimias)
if commandLineOptions.build:
    result = handler.BuildMultiple(handler.GetThirdPartySolutionPaths(), context.GetConfigurationName(), True)
    assert result, "\n\n[CSnake] Task failed: BuildMultiple." 
    print "\n\n[CSnake] Task finished successfully: BuildMultiple.\n"
    result = handler.Build(handler.GetTargetSolutionPath(), context.GetConfigurationName(), False)
    assert result, "\n\n[CSnake] Task failed: Build." 
    print "\n\n[CSnake] Task finished successfully: Build.\n"
    result = handler.InstallBinariesToBuildFolder()
    assert result, "\n\n[CSnake] Task failed: InstallBinariesToBuildFolder." 
    print "\n\n[CSnake] Task finished successfully: InstallBinariesToBuildFolder.\n"

# configure third parties
if commandLineOptions.thirdParty:
    for count in range( 0, context.GetNumberOfThirdPartyFolders() ):
        sourceFolder = context.GetThirdPartyFolder( count )
        buildFolder = context.GetThirdPartyBuildFolders()[ count ]
        taskMsg = "ConfigureThirdPartyFolders from %s to %s..." % (sourceFolder, buildFolder) 
        print "Starting task: " + taskMsg  
    result = handler.ConfigureThirdPartyFolders()
    assert result, "\n\nTask failed: ConfigureThirdPartyFolders." 
    print "Finished " + taskMsg + "\nYou can now build the 3rd party sources.\n"

# install files
if commandLineOptions.install:
    taskMsg = "InstallBinariesToBuildFolder to %s..." % (context.GetBuildFolder())
    print "Starting task: " + taskMsg 
    result = handler.InstallBinariesToBuildFolder()
    assert result, "\n\nTask failed: InstallBinariesToBuildFolder." 
    print "Finished task: " + taskMsg

# configure project
if commandLineOptions.project:
    taskMsg = "ConfigureProjectToBuildFolder to %s..." % (context.GetBuildFolder())
    print "Starting task: " + taskMsg 
    result = handler.ConfigureProjectToBuildFolder(_alsoRunCMake = True, _askUser = askUser)
    assert result, "\n\nTask failed: ConfigureProjectToBuildFolder." 
    print "Finished task: " + taskMsg + "\nYou can now build the sources in %s.\n" % handler.GetTargetSolutionPath()

# guess what to configure (used by cruise control)
if commandLineOptions.autoconfig:
    if context.GetInstance() == "thirdParty":
        print "Starting task: ConfigureThirdPartyFolders."
        result = handler.ConfigureThirdPartyFolders()
        assert result, "\n\nTask failed: ConfigureThirdPartyFolders." 
    else:
        print "Starting task: ConfigureProjectToBuildFolder."
        result = handler.ConfigureProjectToBuildFolder(_alsoRunCMake = True, _askUser = askUser)
        assert result, "\n\nTask failed: ConfigureProjectToBuildFolder." 
        print "Starting task: InstallBinariesToBuildFolder."
        result = handler.InstallBinariesToBuildFolder()
        assert result, "\n\nTask failed: InstallBinariesToBuildFolder." 
    print "Finished task autoconfig."

