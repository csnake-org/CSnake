# Copyright 2007 Pompeu Fabra University (Computational Imaging Laboratory), Barcelona, Spain. Web: www.cilab.upf.edu.
# This software is distributed WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  Script to automate CSnake calls from cruise control

import sys
import csnGUIHandler

# Check command line arguments
if not len(sys.argv) in (2,3):
    sys.exit("Error: not enough arguments. You need to provide a context file and (optionally) an options file.")

if len(sys.argv) == 3:
    print "Converting %s using options file %s\n" % (sys.argv[1], sys.argv[2])
    converter = csnContextConverter(sys.argv[2])
    converter.Convert(sys.argv[1])
    
# Create GUI handler
handler = csnGUIHandler.Handler()
context = handler.LoadContext(sys.argv[1])

# Configure the project
if context.instance == "thirdParty":
    handler.ConfigureThirdPartyFolder()
else:
    handler.ConfigureProjectToBinFolder( True )

