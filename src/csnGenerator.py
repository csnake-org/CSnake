import csnUtility
import csnCMake
import os.path
import warnings
import sys
import types
import OrderedSet
import re
import shutil

# General documentation
#
# This block contains an introduction to the CSnake code. It's main purpose is to introduce some common terminology and concepts.
#  It is assumed that the reader has already read the CSnake user manual.
#
# Terminology:
# dependency project - Project that must also be built in order to built the target project. Modelled by class csnBuild.Project.
# public dependency - If a project A is publicly dependent on B, then projects that are dependent on A will have to include from (and link to)  B.
# build folder - Folder where all intermediate build results (CMakeCache.txt, .obj files, etc) are stored for the target project and all dependency projects.
# binary folder - Folder where all final build results (executables, dlls etc) are stored.
# install folder - Folder to which the build results are copied, and from which you can run the application. Note that CSnake allows you to use the build folder as the install folder as well.
# configuration name - Identifies a build configuration, such as "Debug" or "Release". The name "DebugAndRelease" means that both Debug and Release must be generated.
# source root folder - Folder used for locating the source files for a project. When adding sources to a project, names relative to the source root folder may be used.
#
# Config and use file:
# CMake uses config and use files to let packages use other packages. The config file assigns a number of variables
# such as SAMPLE_APP_INCLUDE_DIRECTORIES and SAMPLE_APP_LIBRARY_DIRECTORIES. The use file uses these values to add
# include directories and library directories to the current CMake target. The standard way to use these files is to a)
# make sure that SAMPLE_APP_DIR points to the location of SAMPLE_APPConfig.cmake and UseSAMPLE_APP.cmake, b) 
# call FIND_PACKAGE(SAMPLE_APP) and c) call INCLUDE(${SAMPLE_APP_USE_FILE}. In step b) the config file of SAMPLE_APP is included and
# in step c) the necessary include directories, library directories etc are added to the current target.
# To adhere to normal CMake procedures, csnBuild also uses the use file and config file. However, FIND_PACKAGE is not needed,
# because the Generator class will directly include the config and use file for any dependency project.
# IMPORTANT: CSnake contains a workaround for a problem in Visual Studio: when you create a dependency, making a project A depend on a B, then Visual Studio will automatically
# link A with the binaries of B. This is a problem, because config file (BConfig.cmake) already tells A to link with the binaries of B, and linking twice with the same binaries may give linker errors.
# To work around this problem, CSnake generates two config files for B: BConfig.cmake and BConfig.cmake.private. The second one does not contain the CMake commands to link with the binaries
# of B, and this config file is included in the CMakeLists.txt of A.
#
# Compilers
#
# In this version of CSnake, you are required to specify the compiler that you will use to build your project. Examples of compiler instances are csnKDevelop.Compiler and csnVisualStudio2003.Compiler.
# I choose this design because it allowed me to simplify the code a lot. For example, when adding a compiler definition for linux, a check is performed to see if the project uses a linux compiler; it not,
# the definition is simply ignored.
# The default compiler is stored in csnProject.globalSettings.compilerType. If you create a Project without specifying a compiler, then this compiler will be assigned to the project instance.
#

# ToDo:
# - Need to add GetDummyCppFilename explicitly?
# - SelectProjects tab should scroll
# - Get rid of prebuiltBinariesFolder
# - Fix bug with /ZM definitions
# - Why fails to add installSubFolder as property?
# - Rename GetOutputFolder to GetBuildResultsFolder
# - Place non-essential fields of csnContext in members such as gui.compiler
# - See which csnProject functions can be removed from the public interface
# - Try to detect compiler location (in a few standard locations) and python location
# - CSnakeGUI should remember al the IDE paths for different ides.
# - Add recently used context files
# - Move cmake path and ide path from context file to options file
# - Build all stuff in DebugAndRelease, Debug or Release. Support DebugAndRelease in Linux by building to both Debug and Release
# - Better GUI: do more checks, give nice error messages, show progress bar (call cmake asynchronous, poll file system) with cancel button. Try catching cmake output using Pexpect
# - Put special file in source root folder. When csn file is selected, check all parent path if they contain this special file and add source root folder.
# - Have public and private related projects (hide the include paths from its clients)
# - If ITK doesn't implement the DONT_INHERIT keyword, then use environment variables to work around the cmake propagation behaviour
# - Fix module reloading
# - Bad smell: Relative paths in _list are assumed to be relative to the third party binary folder. Disallow relative paths? Document in AddFilesToInstall and ResolvePathsOfFilesToInstall
# - Give similar paths similar colours in csnGUI as visual feedback
# - Replace string labels with class types
# End: ToDo.

# add root of csnake to the system path
sys.path.append(csnUtility.GetRootOfCSnake())
version = 2.1

# set default location of python. Note that this path may be overwritten in csnGUIHandler

class SyntaxError(StandardError):
    """ Used when there is a syntax error, for example in a folder name. """
    pass

def ToProject(project):
    """
    Helper function that tests if its argument (project) is a function. If so, it returns the result of the function. 
    If not, it returns its argument (project). It is used to treat Project instances and functions returning a Project instance
    in the same way.
    """
    result = project
    if type(project) == types.FunctionType:
        result = project()
    return result
    
class Generator:
    """
    Generates the CMakeLists.txt for a csnBuild.Project and all its dependency projects.
    """

    def __init__(self):
        pass
        
    def Generate(self, _targetProject, _generatedList = None):
        """
        Generates the CMakeLists.txt for _targetProject (a csnBuild.Project) in the build folder.
        _generatedList -- List of projects for which Generate was already called (internal to the function).
        """

        _targetProject.dependenciesManager.isTopLevel = _generatedList is None
        if _targetProject.dependenciesManager.isTopLevel:
            _generatedList = []

        # assert that this project is not filtered
        assert not _targetProject.MatchesFilter(), "\n\nLogical error: the project %s should have been filtered instead of generated." % _targetProject.name
        
        # Trying to Generate a project twice indicates a logical error in the code        
        assert not _targetProject in _generatedList, "\n\nError: Trying to Generate a project twice. Target project name = %s" % (_targetProject.name)

        for generatedProject in _generatedList:
            if generatedProject.name == _targetProject.name:
                raise NameError, "Each project must have a unique name. Conflicting projects are %s (in folder %s) and %s (in folder %s)\n" % (_targetProject.name, _targetProject.GetSourceRootFolder(), generatedProject.name, generatedProject.GetSourceRootFolder())
        _generatedList.append(_targetProject)
        
        # check for backward slashes
        if csnUtility.HasBackSlash(_targetProject.context.buildFolder):
            raise SyntaxError, "Error, backslash found in binary folder %s" % _targetProject.context.buildFolder
        
        # check  trying to build a third party library
        if _targetProject.type == "third party":
            warnings.warn( "CSnake warning: you are trying to generate CMake scripts for a third party module (nothing generated)\n" )
            return
         
        # create binary project folder
        os.path.exists(_targetProject.GetBuildFolder()) or os.makedirs(_targetProject.GetBuildFolder())
    
        # create Win32Header
        if _targetProject.type != "executable" and _targetProject.GetGenerateWin32Header():
            _targetProject.GenerateWin32Header()
            # add search path to the generated win32 header
            if not _targetProject.GetBuildFolder() in _targetProject.compileManager.public.includeFolders:
                _targetProject.compileManager.public.includeFolders.append(_targetProject.GetBuildFolder())
        
        _targetProject.RunCustomCommands()

        # Find projects that must be generated. A separate list is used to ease debugging.
        projectsToGenerate = OrderedSet.OrderedSet()
        requiredProjects = _targetProject.GetProjects(_recursive = 1, _onlyRequiredProjects = 1)        
        for projectToGenerate in requiredProjects:
            # determine if we must Generate the project. If a required project will generate it, 
            # then leave it to the required project. This will prevent multiple generation of the same project.
            # If a non-required project will generate it, then still generate the project 
            # (the non-required project may depend on target project to generate project, creating a race condition).
            generateProject = not projectToGenerate in _generatedList and projectToGenerate.type in ("dll", "executable", "library")
            if generateProject:
                for requiredProject in _targetProject.GetProjects(_recursive = 0, _onlyRequiredProjects = 1):
                    if requiredProject.DependsOn(projectToGenerate):
                        generateProject = 0
            if generateProject:
                projectsToGenerate.add(projectToGenerate)
        
        # add non-required projects that have not yet been generated to projectsToGenerate
        for project in _targetProject.GetProjects(_onlyNonRequiredProjects = True):
            if not project in _generatedList:
                projectsToGenerate.add(project)

        # generate projects, and add a line with ADD_SUBDIRECTORY
        generatedProjects = OrderedSet.OrderedSet()
        for project in projectsToGenerate:
            # check again if a previous iteration of this loop didn't add project to the generated list
            if not project in _generatedList:
                self.Generate(project, _generatedList)
                generatedProjects.append(project)
           
        # write cmake files
        writer = csnCMake.Writer(_targetProject)
        writer.GenerateConfigFile( _public = 0)
        writer.GenerateConfigFile( _public = 1)
        writer.GenerateUseFile()
        writer.GenerateCMakeLists(generatedProjects, requiredProjects, _writeInstallCommands = _targetProject.dependenciesManager.isTopLevel)

    def InstallBinariesToBinFolder(self, _targetProject):
        """ 
        This function copies all third party dlls to the binary folder, so that you can run the executables in the
        binary folder without having to build the INSTALL target.
        """
        result = True
        _targetProject.ResolvePathsOfFilesToInstall()
        
        for mode in ("Debug", "Release"):
            outputFolder = _targetProject.context.GetOutputFolder(mode)
            os.path.exists(outputFolder) or os.makedirs(outputFolder)
            for project in _targetProject.GetProjects(_recursive = 1, _includeSelf = True):
                for location in project.installManager.filesToInstall[mode].keys():
                    for file in project.installManager.filesToInstall[mode][location]:
                        absLocation = "%s/%s" % (outputFolder, location)
                        assert not os.path.isdir(file), "\n\nError: InstallBinariesToBinFolder cannot install a folder (%s)" % file
                        os.path.exists(absLocation) or os.makedirs(absLocation)
                        assert os.path.exists(absLocation), "Could not create %s\n" % absLocation
                        fileResult = (0 != shutil.copy(file, absLocation))
                        result = fileResult and result
                        if not fileResult:
                            print "Failed to copy %s to %s\n" % (file, absLocation)
        return result
                        
    def PostProcess(self, _targetProject):
        """
        Apply post-processing after the CMake generation for _targetProject and all its child projects.
        """
        for project in _targetProject.GetProjects(_recursive = 1, _includeSelf = True):
            _targetProject.context.postProcessor.Do(project)
