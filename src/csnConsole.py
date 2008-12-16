import csnGUIHandler
import csnGenerator
import csnContext

handler = csnGUIHandler.Handler()
context = handler.LoadContext("./settings.CSnake")

if True:
    taskMsg = "ConfigureThirdPartyFolder from %s to %s..." % (context.thirdPartyRootFolder, context.thirdPartyBinFolder) 
    print "Starting task: " + taskMsg  
    result = handler.ConfigureThirdPartyFolder()
    assert result, "\n\nTask failed: ConfigureThirdPartyFolder" 
    print "Finished " + taskMsg + "\nPlease build the 3rd party sources then press enter...\n"
    raw_input()

taskMsg = "InstallBinariesToBinFolder to %s..." % (context.buildFolder)
print "Starting task: " + taskMsg 
result = handler.InstallBinariesToBinFolder()
assert result, "\n\nTask failed: InstallBinariesToBinFolder" 
print "Finished task: " + taskMsg

taskMsg = "ConfigureProjectToBinFolder to %s..." % (context.buildFolder)
print "Starting task: " + taskMsg 
result = handler.ConfigureProjectToBinFolder(_alsoRunCMake = True)
assert result, "\n\nTask failed: ConfigureProjectToBinFolder" 
print "Finished task: " + taskMsg + "\nPlease build the sources in %s.\n" % handler.GetTargetSolutionPath()
