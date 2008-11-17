import csnUtility
import os.path
import warnings
import sys
import types
import OrderedSet
import ConfigParser
import re

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
# - Try to detect compiler location (in a few standard locations) and python location
# - E&xit
# - Set settings only once in csnGuiHandler
# - Command line option for redirect stdout
# - Simplify Settings.Load and Save by iterating over the member variables and doing a standard load/save
# - Move _configurationName to Settings
# - Apply ExtractMethod on Generate
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

class Settings:
    """
    Contains configuration settings such as source folder/bin folder/etc.
    kdevelopProjectFolder - If generating a KDevelop project, then the KDevelop project file will be
    copied from the bin folder to this folder. This is work around for a problem in 
    KDevelop: it does not show the source tree if the kdevelop project file is in the bin folder.
    """
    def __init__(self):
        self.buildFolder = ""    
        self.installFolder = ""    
        self.kdevelopProjectFolder = ""    
        self.prebuiltBinariesFolder = ""    
        self.thirdPartyBinFolder = ""
        self.csnakeFile = ""
        self.rootFolders = []
        self.thirdPartyRootFolder = ""
        self.instance = ""
        self.testRunnerTemplate = "normalRunner.tpl"
        self.recentlyUsed = list()
        self.filter = ["Demos", "Applications", "Tests"]
            
    def Load(self, filename):
        try:
            parser = ConfigParser.ConfigParser()
            parser.read([filename])
            self.__LoadBasicFields(parser)
            self.__LoadRootFolders(parser)
            self.__LoadRecentlyUsedCSnakeFiles(parser)
            return 1
        except:
            return 0
        
    def __LoadBasicFields(self, parser):
        section = "CSnake"
        self.buildFolder = parser.get(section, "binFolder")
        self.installFolder = parser.get(section, "installFolder")
        if parser.has_option(section, "kdevelopProjectFolder"):
            self.kdevelopProjectFolder = parser.get(section, "kdevelopProjectFolder")
        if parser.has_option(section, "prebuiltBinariesFolder"):
            self.prebuiltBinariesFolder = parser.get(section, "prebuiltBinariesFolder")
        self.thirdPartyBinFolder = parser.get(section, "thirdPartyBinFolder")
        self.csnakeFile = parser.get(section, "csnakeFile")
        self.thirdPartyRootFolder = parser.get(section, "thirdPartyRootFolder")
        self.instance = parser.get(section, "instance")
        if parser.has_option(section, "filter"):
            self.filter = re.split(";", parser.get(section, "filter"))
        if parser.has_option(section, "testRunnerTemplate"):
            self.testRunnerTemplate = parser.get(section, "testRunnerTemplate")

    def __LoadRootFolders(self, parser):
        section = "RootFolders"
        count = 0
        self.rootFolders = []
        print "Searching for %s\n" % section
        while parser.has_option(section, "RootFolder%s" % count):
            print "Found %s\n" % section
            self.rootFolders.append( parser.get(section, "RootFolder%s" % count) )
            count += 1
        
    def __LoadRecentlyUsedCSnakeFiles(self, parser):
        self.recentlyUsed = []
        count = 0
        section = "RecentlyUsedCSnakeFile%s" % count
        while parser.has_section(section):
            self.AddRecentlyUsed(parser.get(section, "instance"), parser.get(section, "csnakeFile"))
            count += 1
            section = "RecentlyUsedCSnakeFile%s" % count
    
    def __SaveRecentlyUsedCSnakeFiles(self, parser):
        for index in range(len(self.recentlyUsed)):
            section = "RecentlyUsedCSnakeFile%s" % index
            if not parser.has_section(section):
                parser.add_section(section)
            parser.set(section, "csnakeFile", self.recentlyUsed[index].csnakeFile) 
            parser.set(section, "instance", self.recentlyUsed[index].instance) 

    def AddRecentlyUsed(self, _instance, _csnakeFile):
        for item in range( len(self.recentlyUsed) ):
            x = self.recentlyUsed[item]
            if (x.instance == _instance and x.csnakeFile == _csnakeFile):
                self.recentlyUsed.remove(x)
                self.recentlyUsed.insert(0, x)
                return
        
        x = Settings()
        (x.instance, x.csnakeFile) = (_instance, _csnakeFile)
        self.recentlyUsed.insert(0, x)
        if len(self.recentlyUsed) > 10:
            self.recentlyUsed.pop() 
    
    def Save(self, filename):
        parser = ConfigParser.ConfigParser()
        section = "CSnake"
        rootFolderSection = "RootFolders"
        parser.add_section(section)
        parser.add_section(rootFolderSection)

        parser.set(section, "binFolder", self.buildFolder)
        parser.set(section, "installFolder", self.installFolder)
        parser.set(section, "kdevelopProjectFolder", self.kdevelopProjectFolder)
        parser.set(section, "prebuiltBinariesFolder", self.prebuiltBinariesFolder)
        parser.set(section, "thirdPartyBinFolder", self.thirdPartyBinFolder)
        parser.set(section, "csnakeFile", self.csnakeFile)
        parser.set(section, "filter", ";".join(self.filter))
        count = 0
        while count < len(self.rootFolders):
            parser.set(rootFolderSection, "RootFolder%s" % count, self.rootFolders[count] )
            count += 1
        parser.set(section, "thirdPartyRootFolder", self.thirdPartyRootFolder)
        parser.set(section, "instance", self.instance)
        parser.set(section, "testRunnerTemplate", self.testRunnerTemplate)
        
        self.__SaveRecentlyUsedCSnakeFiles(parser)
        
        f = open(filename, 'w')
        parser.write(f)
        f.close()
    
class Generator:
    """
    Generates the CMakeLists.txt for a csnBuild.Project and all its dependency projects.
    """

    def __init__(self, settings):
        self.settings = settings
        
    def Generate(self, _targetProject, _configurationName = "DebugAndRelease", _generatedList = None):
        """
        Generates the CMakeLists.txt for _targetProject (a csnBuild.Project) in the build folder.
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
        if csnUtility.HasBackSlash(self.settings.buildFolder):
            raise SyntaxError, "Error, backslash found in binary folder %s" % self.settings.buildFolder
        
        # check  trying to build a third party library
        if _targetProject.type == "third party":
            warnings.warn( "CSnake warning: you are trying to generate CMake scripts for a third party module (nothing generated)\n" )
            return
         
        # set build folder in all compiler instances
        if isTopLevelProject:
            _targetProject.compiler.SetBuildFolder(self.settings.buildFolder)
            for project in _targetProject.GetProjects(_recursive = True):
                project.compiler.SetBuildFolder(self.settings.buildFolder)
                
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
        _targetProject.CreateCMakeSections(f, self.settings.installFolder)

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
                self.Generate(project, _configurationName, _generatedList)
           
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
                            destination = "%s/%s" % (self.settings.installFolder, location)
                            f.write( "\n# Rule for installing files in location %s\n" % destination)
                            f.write("INSTALL(FILES %s DESTINATION \"%s\" CONFIGURATIONS %s)\n" % (files, destination, mode.upper()))
                        
        f.close()
        csnUtility.ReplaceDestinationFileIfDifferentAndSaveBackup(tmpCMakeListsFile, _targetProject.GetCMakeListsFilename())

    def PostProcess(self, _targetProject):
        """
        Apply post-processing after the CMake generation for _targetProject and all its child projects.
        """
        for project in _targetProject.GetProjects(_recursive = 1, _includeSelf = True):
            _targetProject.compiler.GetPostProcessor().Do(project, self.settings.buildFolder, self.settings.kdevelopProjectFolder)
