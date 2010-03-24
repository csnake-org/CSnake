#!/bin/sh
# --------------------------
# Run the csnake tests
# --------------------------

# Add csnake src to the python path
set PYTHONPATH=../src;./src
# Run all tests
python AllTests.py
