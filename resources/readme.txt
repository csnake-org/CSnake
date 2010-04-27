--------------
CSnake readme
--------------

Version: 2.3.0

Change log
----------

v2.3.0:

 * Multiple source / third party folders
 * Added automated tests for main functionalities
 * Automatic building of executable for windows
 * Updated to Python 2.5/2.6 standard
 * Automatic find default Visual Studio path: when selecting the compiler, 
   it will search the windows registry to find the installation folder. (windows)
 * Double click to access folder browser (windows)
 * Automatically configure thirdparty folders when adding a Gimias root folder
 * Configure all: one click to: Configure third party / Build third party / Configure CMake files / Build CMake files / Install files to build folder 

Bug fix

 * CSnake build type (0004): The CSnake build type 'Release' and 'Debug' do not 
   work when compiling under Windows, only the 'DebugAndRelease?' does. 
   Either fix it or remove the option. Under Linux, it is not propagated to CMake 
   for the first build and needs to be set manually. 


Installation
------------
Double click on the 'CSnake-*.*.*-Setup.exe' and follow instructions.

Running
-------
A 'CSnake' shortcut should be available in the 'start' menu. Otherwise, locate the installation folder and run
the 'csnGUI.exe' file.

Uninstalling
------------
A 'Uninstall CSnake' shortcut should be available in the 'start' menu. Otherwise, locate the installation folder and run
the 'uninstall.exe' file.
