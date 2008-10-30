import csnUtility
import os.path
import warnings
import sys
import types
import OrderedSet

# General documentation
#
# This block contains an introduction to the CSnake code. It's main purpose is to introduce some common terminology and concepts.
#  It is assumed that the reader has already read the CSnake user manual.
#
# Terminology:
# target project - Project that you want to build with CSnake. Modelled by class csnBuild.Project.
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
#
# Compilers
#
# In this version of CSnake, you are required to specify the compiler that you will use to build your project. Examples of compiler instances are csnKDevelop.Compiler and csnVisualStudio2003.Compiler.
# I choose this design because it allowed me to simplify the code a lot. For example, when adding a compiler definition for linux, a check is performed to see if the project uses a linux compiler; it not,
# the definition is simply ignored.
# The default compiler is stored in csnBuild.globalSettings.compilerType. If you create a Project without specifying a compiler, then this compiler will be assigned to the project instance.
#

# ToDo:
# - check that of all root folders, only one contains csnCISTIBToolkit
# - Have public and private related projects (hide the include paths from its clients)
# - If ITK doesn't implement the DONT_INHERIT keyword, then use environment variables to work around the cmake propagation behaviour
# - csn python modules can contain option widgets that are loaded into CSnakeGUI! Use this to add selection of desired toolkit modules in csnGIMIAS
# - Fix module reloading
# - Better GUI: do more checks, give nice error messages
# - If copy_tree copies nothing, check that the source folder is empty
# - Run CMake in parallel on independent configuration steps
# End: ToDo.

# add root of csnake to the system path
sys.path.append(csnUtility.GetRootOfCSnake())
version = 1.24

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

    def Generate(self, _targetProject, _buildFolder, _installFolder = "", _configurationName = "DebugAndRelease", _generatedList = None):
        """
        Generates the CMakeLists.txt for _targetProject (a csnBuild.Project) in _buildFolder.
        _installFolder -- Install rules are added to the CMakeLists to install files in this folder.
        _configurationName -- If "DebugAndRelease", then a Debug and a Release configuration are generated (works with Visual Studio),
        if "Debug" or "Release", then only a single configuration is generated (works with KDevelop and Unix Makefiles).
        _generatedList -- List of projects for which Generate was already called (internal to the function).
        """

        isTopLevelProject = _generatedList is None
        if isTopLevelProject:
            _generatedList = []

        # assert that this project is not filtered
        assert not _targetProject.MatchesFilter(), "\n\nLogical error: the project %s should have been filtered instead of generated." % _targetProject.name
        
        # Trying to Generate a project twice indicates a logical error in the code        
        assert not _targetProject in _generatedList, "\n\nError: Trying to Generate a project twice. Target project name = %s" % (_targetProject.name)

        for generatedProject in _generatedList:
            if generatedProject.name == _targetProject.name:
                raise NameError, "Each project must have a unique name. Conflicting projects are %s (in folder %s) and %s (in folder %s)\n" % (_targetProject.name, _targetProject.sourceRootFolder, generatedProject.name, generatedProject.sourceRootFolder)
        _generatedList.append(_targetProject)
        
        # check for backward slashes
        if csnUtility.HasBackSlash(_buildFolder):
            raise SyntaxError, "Error, backslash found in binary folder %s" % _buildFolder
        
        # check  trying to build a third party library
        if _targetProject.type == "third party":
            warnings.warn( "CSnake warning: you are trying to generate CMake scripts for a third party module (nothing generated)\n" )
            return
         
        # set build folder in all compiler instances
        if isTopLevelProject:
            _targetProject.compiler.SetBuildFolder(_buildFolder)
            for project in _targetProject.GetProjects(_recursive = True):
                project.compiler.SetBuildFolder(_buildFolder)
                
        # create binary project folder
        os.path.exists(_targetProject.GetBuildFolder()) or os.makedirs(_targetProject.GetBuildFolder())
    
        # create Win32Header
        if _targetProject.type != "executable" and _targetProject.GetGenerateWin32Header():
            _targetProject.GenerateWin32Header()
            # add search path to the generated win32 header
            if not _targetProject.GetBuildFolder() in _targetProject.compiler.public.includeFolders:
                _targetProject.compiler.public.includeFolders.append(_targetProject.GetBuildFolder())
        
        # open cmakelists.txt
        tmpCMakeListsFile = _targetProject.GetCMakeListsFilename() + ".tmp"
        f = open(tmpCMakeListsFile, 'w')
        
        # write header and some cmake fields
        f.write( "# CMakeLists.txt generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "PROJECT(%s)\n" % (_targetProject.name) )
        f.write( "SET( BINARY_DIR \"%s\")\n" % (_targetProject.compiler.GetOutputFolder(_configurationName)) )

        if not _configurationName == "DebugAndRelease":
            f.write( "SET( CMAKE_BUILD_TYPE %s )\n" % (_configurationName) )
        
        f.write( "\n# All binary outputs are written to the same folder.\n" )
        f.write( "SET( CMAKE_SUPPRESS_REGENERATION TRUE )\n" )
        f.write( "SET( EXECUTABLE_OUTPUT_PATH \"%s\")\n" % _targetProject.GetBinaryInstallFolder(_configurationName) )
        f.write( "SET( LIBRARY_OUTPUT_PATH \"%s\")\n" % _targetProject.GetBinaryInstallFolder(_configurationName) )
    
        # create config and use files, and include them
        _targetProject.GenerateConfigFile( _public = 0)
        _targetProject.GenerateConfigFile( _public = 1)
        _targetProject.GenerateUseFile()
        
        _targetProject.RunCustomCommands()
        _targetProject.CreateCMakeSections(f, _installFolder)

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
        f.write( "\n" )
        
        # add non-required projects that have not yet been generated to projectsToGenerate
        for project in _targetProject.projectsNonRequired:
            if not project in _generatedList:
                projectsToGenerate.add(project)

        # generate projects, and add a line with ADD_SUBDIRECTORY
        for project in projectsToGenerate:
            # check again if a previous iteration of this loop didn't add project to the generated list
            if not project in _generatedList:
                f.write( "ADD_SUBDIRECTORY(\"%s\" \"%s\")\n" % (project.GetBuildFolder(), project.GetBuildFolder()) )
                self.Generate(project, _buildFolder, _installFolder, _configurationName, _generatedList)
           
        # add dependencies
        f.write( "\n" )
        for project in requiredProjects:
            staticLibUsingAnotherLib = _targetProject.type == "library" and project.type != "executable" 
            noSources = len(project.sources) == 0 
            if (csnUtility.IsRunningOnWindows() and staticLibUsingAnotherLib) or noSources: 
                continue
            else:
                f.write( "ADD_DEPENDENCIES(%s %s)\n" % (_targetProject.name, project.name) )

        # if top level project, add install rules for all the filesToInstall
        if isTopLevelProject:
            for mode in ("Debug", "Release"):
                for project in _targetProject.ProjectsToUse():
                    # iterate over filesToInstall to be copied in this mode
                    for location in project.filesToInstall[mode].keys():
                        files = ""
                        for file in project.filesToInstall[mode][location]:
                            files += "%s " % csnUtility.NormalizePath(file)
                        if files != "":
                            destination = "%s/%s" % (_installFolder, location)
                            f.write( "\n# Rule for installing files in location %s\n" % destination)
                            f.write("INSTALL(FILES %s DESTINATION \"%s\" CONFIGURATIONS %s)\n" % (files, destination, mode.upper()))
                        
        f.close()
        csnUtility.ReplaceDestinationFileIfDifferentAndSaveBackup(tmpCMakeListsFile, _targetProject.GetCMakeListsFilename())

    def PostProcess(self, _targetProject, _buildFolder, _kdevelopProjectFolder = ""):
        """
        Apply post-processing after the CMake generation for _targetProject and all its child projects.
        _kdevelopProjectFolder - If generating a KDevelop project, then the KDevelop project file will be
        copied from the bin folder to this folder. This is work around for a problem in 
        KDevelop: it does not show the source tree if the kdevelop project file is in the bin folder.
        """
        for project in _targetProject.GetProjects(_recursive = 1, _includeSelf = True):
            _targetProject.compiler.GetPostProcessor().Do(project, _buildFolder, _kdevelopProjectFolder)
     
