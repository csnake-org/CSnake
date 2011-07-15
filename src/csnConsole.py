## @package csnConsole
# Command line interface for CSnake. 
import csnGUIHandler
import sys
from optparse import OptionParser
import os.path

parser = OptionParser(usage="%prog contextFile [options]")
parser.add_option("-i", "--install", dest="install", action="store_true", default=False, help="install files to build folder")
parser.add_option("-t", "--thirdParty", dest="thirdParty", action="store_true", default=False, help="configure third party projects")
parser.add_option("-p", "--project", dest="project", action="store_true", default=False, help="configure project")
parser.add_option("-c", "--configure", action="store_true", default=False, help="configure all")
parser.add_option("-b", "--build", action="store_true", default=False, help="build all")
parser.add_option("-a", "--autoconfig", dest="autoconfig", action="store_true", default=False, help="configure third party or project depending on the context instance")
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

# configure third parties and project (used by Gimias)
if commandLineOptions.configure:
    handler.ConfigureThirdPartyFolders()
    handler.ConfigureProjectToBuildFolder(_alsoRunCMake = True)

# build third parties and project + install files (used by Gimias)
if commandLineOptions.build:
    handler.BuildMultiple(handler.GetThirdPartySolutionPaths(), context.GetConfigurationName(), True)
    handler.Build(handler.GetTargetSolutionPath(), context.GetConfigurationName(), False)
    handler.InstallBinariesToBuildFolder()

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
    result = handler.ConfigureProjectToBuildFolder(_alsoRunCMake = True)
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
        result = handler.ConfigureProjectToBuildFolder(_alsoRunCMake = True)
        assert result, "\n\nTask failed: ConfigureProjectToBuildFolder." 
        print "Starting task: InstallBinariesToBuildFolder."
        result = handler.InstallBinariesToBuildFolder()
        assert result, "\n\nTask failed: InstallBinariesToBuildFolder." 
    print "Finished task autoconfig."
