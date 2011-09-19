## @package csnBuildTests
# Definition of the csnBuildTests class.
# \ingroup tests
import os.path
import csnProject
import csnGUIHandler
import shutil
import subprocess

def testBuild(testConfig):
    """
    Build test: will try to configure, compile and test example project from the tests/data folder.
    Depends on local machine configuration, please create a tests/config/csnake_context.txt based on the
    following lines:

# Specific project settings
csnakefile = PATH_TO_CSNAKE/tests/data
instance = 
prebuiltBinariesFolder = 
kdevelopProjectFolder = 

# Toolkit settings
filter = *Demos
testrunnertemplate = xmlRunner.tpl
installfolder = PATH_TO_CSNAKE/tests
buildfolder = PATH_TO_CSNAKE/tests

# Compilation settings
compilername = Visual Studio 10 Win64
configurationname = DebugAndRelease

# General settings
pythonpath = C:/Program Files/Python27/python.exe
cmakepath = C:/Program Files (x86)/CMake 2.8/bin/cmake.exe
idepath = C:/Program Files (x86)/Microsoft Visual Studio 10.0/Common7/IDE/devenv.exe
version = 2.1

[RootFolders]
rootfolder0 = PATH_TO_CSNAKE/tests/data

[ThirdPartyFolders]
thirdpartyfolder0 = PATH_TO_CSNAKE/tests/data

[ThirdPartyBuildFolders]
thirdpartybuildfolder0 = PATH_TO_CSNAKE/tests
    """
    
    # create the context file
    testConfig.createContext()
    
    # create GUI handler
    handler = csnGUIHandler.Handler()
    # load context
    context = handler.LoadContext(testConfig.getContextFileName())
    
    # configure and compile third parties
    ret = handler.ConfigureThirdPartyFolders()
    assert ret == True, "CMake returned with an error message while configuring the third parties."
    
    # compile third parties
    
    if( context.GetCompilername().find("Visual Studio") != -1 ):
        for index in range(0,context.GetNumberOfThirdPartyFolders()):
            # create compiler command
            compileArgList = []
            # compiler
            compileArgList.append(context.GetIdePath())
            # solution file
            solutionFile = "%s/CILAB_TOOLKIT.sln" % context.GetThirdPartyBuildFolderByIndex(index)
            assert os.path.exists(solutionFile), "The third party solution file does not exist."
            compileArgList.append(solutionFile)
            # build mode
            mode = "%s|x64" % testConfig.getBuildMode()
            compileArgList.append("/build")
            compileArgList.append(mode)
            # build path
            buildPath = testConfig.getTpBinDirs()[index]
            # run compiler
            ret = subprocess.call(compileArgList, cwd=buildPath)
            assert ret == 0, "The compiler returned with an error message while compiling the third parties."
        
    elif( context.GetCompilername().find("KDevelop3") != -1 or
          context.GetCompilername().find("Makefile") != -1 ):
        for index in range(0,context.GetNumberOfThirdPartyFolders()):
            # create compiler command
            compileArgList = []
            # build path
            buildPath = context.GetThirdPartyBuildFolderByIndex(index)
            # make
            compileArgList.append("make")
            compileArgList.append("-s")
            # run compiler (cwd needed for make)
            ret = subprocess.call(compileArgList, cwd=buildPath)
            assert ret == 0, "The compiler returned with an error message while compiling the third parties."
    
    # install files to bin folder
    ret = handler.InstallBinariesToBuildFolder()
    # check that it worked
    assert ret == True, "Installing binaries to build folder failed."
    
    # configure the project
    runCsnake = True
    ret = handler.ConfigureProjectToBuildFolder( runCsnake )        
    # check that it worked
    assert ret == True, "CMake returned with an error message while configuring the project."
    
    # compile project
    
    # create compiler command
    compileArgList = []
    if( context.GetCompilername().find("Visual Studio") != -1 ):
        # build path
        buildPath = "%s/%s" % (testConfig.getBuildPath(), testConfig.getName())
        # compiler
        compileArgList.append(context.GetIdePath())
        # solution file
        solutionFile = handler.GetTargetSolutionPath()
        assert os.path.exists(solutionFile), "The project solution file does not exist."
        compileArgList.append(solutionFile)
        # build mode
        mode = "%s|x64" % testConfig.getBuildMode()
        compileArgList.append("/build")
        compileArgList.append(mode)
    elif( context.GetCompilername().find("KDevelop3") != -1 or
          context.GetCompilername().find("Makefile") != -1 ):
        # build path
        buildPath = "%s/%s/%s" % (testConfig.getBuildPath(), testConfig.getBuildMode(), testConfig.getName())
        # make
        compileArgList.append("make")
        compileArgList.append("-s")
    
    # run compiler (cwd needed for make)
    ret = subprocess.call(compileArgList, cwd=buildPath)
    assert ret == 0, "The compiler returned with an error message while compiling the project."

    # check the built executable
    exeFilename = "%s/bin/%s/%s" % (context.GetBuildFolder(), testConfig.getBuildMode(), testConfig.getExeName())
    if( context.GetCompilername().find("Visual Studio") != -1 ):
        exeFilename = "%s.exe" % (exeFilename)
    assert os.path.exists(exeFilename)
    
    # test the built executable
    ret = subprocess.call(exeFilename)
    assert ret == 6, "The generated executable did not return the correct result."

    # run tests with lib
    if testConfig.getType() == "lib":
        # check the built test
        testName = testConfig.getName() + "Tests"
        testExeFilename = "%s/bin/%s/%s" % (context.GetBuildFolder(), testConfig.getBuildMode(), testName)
        if( context.GetCompilername().find("Visual Studio") != -1 ):
            testExeFilename = "%s.exe" % (testExeFilename)
        assert os.path.exists(testExeFilename)
        
        # run the test
        ret = subprocess.call(testExeFilename)
        assert ret == 0, "The generated test did not return the correct result."
    
    # clean up
    shutil.rmtree( csnProject.globalCurrentContext.GetBuildFolder() )
    os.remove(testConfig.getContextFileName())
