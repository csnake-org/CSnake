--------------
CSnake readme
--------------

Version: 2.4.2

Change log
----------

v2.4.2
 * Bug: Generate CLP warning
 
v2.4.1
 * Bug: Windows7 compatibility mode
 * Bug: CSnake sleeps forever, if thirdParties have not been configured
 * Bug: Exceptions does not stop process pipeline
 * Mac error when using found paths
 * Add Visual Studio 10 compiler
 * Remove third party double configuration
 * Instance update with same csn file

v2.4.0
 * Bug: Visual studio express error
 * Bug: Combo box not working
 * Bug: Csnake configuration gives error
 * Gimias command line plugin
 * Pch for tests
 * Add tests for context and option file reading
 * Automatic options search
 * Instance list update
 * Context file name extension
 * File save behaviour
 * Application file location
 * Remove direct calls to print

v2.3.3
 * Fix install files after configure third parties 

v2.3.2

 * Fix dependency mechanism (linux build failures)
 * Fix multiple src/third party folder support for linux
 * Fix install files to build folder for multiple src/third party

Note: 
- csn files of third parties should not use the {{{project.context.GetThirdPartyBuildFolder()}}} but 
the {{{project.GetBuildFolder()}}} method, the first one gives you one of the third party folders 
and the second one gives you the specific one of your third party. This was changed in version 1.1.0 of the 
toolkit. Project using the first method can be configured only if the toolkit third parties are first in the list.
- be carefull: all thrid party source folder should have a specific associated bin folder (they cannot use the same one)

v2.3.1

 * Changed application folder to lower case a (still working for both cases)
 * Reverted application suffix to old one (Applications)

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
