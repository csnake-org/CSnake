# Copyright 2007 Pompeu Fabra University (Computational Imaging Laboratory), Barcelona, Spain. Web: www.cilab.upf.edu.
# This software is distributed WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  Script to automate CSnake calls from cruise control

import sys
import csnGUIHandler
import csnGUIOptions
import csnGenerator

# Check command line arguments
if len(sys.argv) != 3:
    sys.exit("Error: not enough arguments. You need to provide an option and a configuration file.")

# Command line inputs
options_file = sys.argv[1]
config_file = sys.argv[2]

# Create GUI handler
handler = csnGUIHandler.Handler()
# Read options
options = csnGUIOptions.Options()
options.Load( options_file )
# Read settings
settings = csnGenerator.Settings()
settings.Load( config_file )
# Set the options
handler.SetOptions( options )
# Configure the project with the settings
if settings.instance == "thirdParty":
    handler.ConfigureThirdPartyFolder(settings)
else:
    handler.ConfigureProjectToBinFolder( settings, 1 )

