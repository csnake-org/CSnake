#!/bin/sh
# --------------------------
# Run the csnake tests
# --------------------------

# Theses test depend on a context file specific to your machine.
# They expect it to be: ./config/csnake_context.txt
# You can use the template one of this folder and replace with your settings.
# Important options:
#  rootfolder0 = %PATH_TO_TEST_SRC%
#  csnakefile = %rootfolder0%/TestInstance/csnTestInstance.py
#  instance = testInstance
#  thirdpartyrootfolder = %rootfolder0%/src
# Build and install folders are created and deleted at the end of the tests

# Add csnake src to the python path
export PYTHONPATH=$PYTHONPATH:../src:./src
# Run all tests
python AllTests.py
