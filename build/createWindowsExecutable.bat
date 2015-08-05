@echo off
REM ------------------------------------
REM Generate an executable for CSnake
REM ------------------------------------

REM Call py2exe
REM Needs msvcp90.dll
REM  (I had to copy it in the running folder...)
python ../src/setup.py py2exe

REM Let us see the results
@pause
