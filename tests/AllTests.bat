@echo off
REM --------------------------
REM Run the csnake tests
REM --------------------------

REM Theses test depend on a context file specific to your machine.
REM They expect it to be: ./config/csnake_context.txt
REM You can use the template one of this folder and replace with your settings.
REM Important options:
REM  rootfolder0 = %PATH_TO_TEST_SRC%
REM  csnakefile = %rootfolder0%/TestInstance/csnTestInstance.py
REM  instance = testInstance
REM  thirdpartyrootfolder = %rootfolder0%/src
REM Build and install folders are created and deleted at the end of the tests

REM Add csnake src to the python path
@set PYTHONPATH=../src;./src
REM Run all tests
@python AllTests.py
REM Let us see the results
@pause
