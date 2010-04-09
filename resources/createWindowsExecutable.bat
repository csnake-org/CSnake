@echo off
REM ------------------------------------
REM Generate an executable fro CSnake
REM ------------------------------------

REM Call py2exe
python ../src/setup.py py2exe

REM Let us see the results
@pause
