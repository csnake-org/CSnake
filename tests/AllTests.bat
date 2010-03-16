@echo off
REM --------------------------
REM Run the csnake tests
REM --------------------------

REM Add csnake src to the python path
@set PYTHONPATH=../src
REM Run all tests
@python AllTests.py
REM Let us see the results
@pause
