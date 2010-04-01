# Copyright 2007 Pompeu Fabra University (Computational Imaging Laboratory), Barcelona, Spain. Web: www.cilab.upf.edu.
# This software is distributed WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  Script to automate CSnake calls from cruise control

import sys
import csnGUIHandler

# Check command line arguments
if len(sys.argv) != 2:
    sys.exit("Error: not enough arguments. You need to provide a context file.")

# Create GUI handler
handler = csnGUIHandler.Handler()
context = handler.LoadContext(sys.argv[1])

# Configure the project
if context.instance == "thirdParty":
    res = handler.ConfigureThirdPartyFolders()
else:
    res = handler.ConfigureProjectToBuildFolder( True )
    handler.InstallBinariesToBuildFolder( )


    
if not res:
    sys.exit("Error configuring instance %s" % context.instance)
