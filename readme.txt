--------------
CSnake readme
--------------
CSnake is a build system based on CMake. It is meant to simplify the configuration 
process of libraries. It was initially developed by the 
Center for Computational Imaging & Simulation Technologies In Biomedicine (CISTIB), 
based in Barcelona, Spain. 
It is mainly used to configure the building of the GIMIAS (http://www.gimias.org/) software.

More information can be found on https://github.com/csnake-org/CSnake.

Change log
----------
v2.5.0
 * API: creation of the CSnake API
 * Line endings: regularise
 * Activate alt shortcuts in menu
 * Separate CISTIB-specific from generic code in csnCilab.py
 * Version Numbers: better handling
 * Dependencies in "Select Projects" tab: show dependent projects
 * Optimization: speed optimizations
 * KDevelop Project Folder: removed panel
 * Don't deactivate buttons in GUI
 * Verify text box content before launching actions
 * Instead of '*.compileManager.generateWin32Header = False' use '*.SetGenerateWin32Header(False)'
 * FIX: API: Bug in CreateHeader(Do)
 * FIX: API: Bug in RewrapProject
 * FIX: Keep compatibility with python 2.6
 * FIX: Switching between 32Bit and 64Bit version of the same context file doesn't work

v2.4.4
 * Add support for cmake 2.8.5
 * Add a 'New' menu item in the file menu
 * Install files to check file dates
 * Select Projects tree
 * Errors from launching the select project tab could be more explicit
 * Remove wx dependency for console run
 * Sort console mode
 * Fix hanging progress bar (...)
 * Add package documentation
 * Bug: Cannot load context with bad compiler
 * Bug: Catch parsing error when loading option file
 * Bug: Prevent asking to launch ide when doing a configure all
 * Bug: Check existence of context file in console mode
 * Bug: csnConsole --thirdParty does not work
 * ENH: Allow to create tests for plugins with delay load
 * ENH: Allow to add properties for a target

v2.4.3
 * Save recent context files
 * Add support for drag and drop of context files
 * Add CTest creation to the projects
 * Add configure and build option from the command line
 * Add links to doxygen main page
 * Automatic bin folder for thirdParty
 * Add progress bar for single third party configuration
 * Plugin only solution
 * Add a plugin category in project list
 * Use minutes for times
 * Bug: Auto Launch IDE does not work for project
 * Bug: Ask to launch IDE check box is not saved
 * Switch to Git

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
 * File save behavior
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
- be careful: all third party source folder should have a specific associated bin folder (they cannot use the same one)

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
On Windows, double click on the 'CSnake-*.*.*-Setup.exe' and follow instructions.
For the other platforms, sorry no automatic installation is provided.

Running
-------
On Windows, a 'CSnake' shortcut should be available in the 'start' menu. 
Otherwise, locate the installation folder and run the 'csnGUI.exe' file.

Uninstalling
------------
On Windows, an 'Uninstall CSnake' shortcut should be available in the 'start' menu. Otherwise, 
locate the installation folder and run the 'uninstall.exe' file.
For the other platforms, sorry no automatic uninstall is provided, just delete the folder. 
Local information is stored in the user's folder under '.csnake'.
