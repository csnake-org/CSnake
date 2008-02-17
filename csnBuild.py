from os import makedirs
import csnUtility
import os.path
import warnings
import sys
import re
import glob
import traceback

# ToDo:
# - Have public and private related projects (hide the include paths from its clients)
# - Unloading all modules in csnCilab.LoadModule does not work (it will reload the >cached< module). 
# This makes it impossible to use changed csn files while the GUI is still running. 
# Need to replace the 'imp' approach. 
# Look at RollBackImporter (http://www.koders.com/python/fid3017018D7707B26F40B546EE2D1388C1A14383D3.aspx?s=%22Steve+Purcell%22)
# - If ITK doesn't implement the DONT_INHERIT keyword, then use environment variables to work around the cmake propagation behaviour
# - Support precompiled headers by patching the produces vcproj files
# - csn python modules can contain option widgets that are loaded into CSnakeGUI! Use this to add
# selection of desired toolkit modules in csnGIMIAS
# - create convenience module csnCilabAll with attributes itk, vtk, baselib, etc.
# - install msvcp.dll and mitkstatemachine.xml
# - extend csnGUI with the option of additional root folders
# - support installing subtrees to the binfolder, so that the cardiacplugin functions correctly 
# (it needs bin/debug/plugins/cardiacsegmpl/data)


root = "%s/.." % (os.path.dirname(__file__))
root = root.replace("\\", "/")
if( not root in sys.path ):
    sys.path.append(root)

class DependencyError(StandardError):
    pass
    
class SyntaxError(StandardError):
    pass

class ProjectClosedError(StandardError):
    pass
    
def Caller(up=0):
    """
    Get file name, line number, function name and
    source text of the caller's caller as 4-tuple:
    (file, line, func, text).
    The optional argument 'up' allows retrieval of
    a caller further back up into the call stack.
    """
    f = traceback.extract_stack(limit=up+2)
    return f[0]
        
class OpSysSection:
    """ 
    Helper class for OpSys 
    """
    def __init__(self):
        self.definitions = list()
        self.libraries = list()
        self.includeFolders = list()
        self.libraryFolders = list()

class OpSys:
    """ 
    Helper class that contains the settings on an operating system 
    """
    def __init__(self):
        self.public = OpSysSection()
        self.private = OpSysSection()
            
class Generator:
    """
    Generates the CMakeLists.txt for a csnBuild.Project.
    """

    def Generate(self, _targetProject, _binaryFolder, _installFolder = "", _generatedList = None, _knownProjectNames = None):
        """
        Generates the CMakeLists.txt for a csnBuild.Project in _binaryFolder.
        All binaries are placed in _binaryFolder/bin.
        _binaryFolder -- Target location for the cmake files.
        _generatedList -- List of projects for which Generate was already called
        """

        isTopLevelProject = _generatedList is None
        if( _generatedList is None ):
            _generatedList = []

        if( _knownProjectNames is None ):
            _knownProjectNames = []

        #csnUtility.Log("Generate %s\n" % (_targetProject.name))
        #for project in _generatedList:
        #    csnUtility.Log("Already generated %s\n" % (project.name))
        #csnUtility.Log("---\n")

        if( _targetProject.name in _knownProjectNames):
            raise NameError, "Each project must have a unique name. Violating project is %s in folder %s\n" % (_targetProject.name, _targetProject.sourceRootFolder)
        else:
            _knownProjectNames.append(_targetProject.name)
            
        # trying to Generate a project twice indicates a logical error in the code        
        assert not _targetProject in _generatedList, "Target project name = %s" % (_targetProject.name)
        _generatedList.append(_targetProject)
        
        # check for backward slashes
        if csnUtility.HasBackSlash(_binaryFolder):
            raise SyntaxError, "Error, backslash found in binary folder %s" % _binaryFolder
        
        if( _targetProject.type == "third party" ):
            warnings.warn( "CSnake warning: you are trying to generate CMake scripts for a third party module (nothing generated)\n" )
            return
         
        # this is the OpSys instance for all operating systems
        opSysAll = _targetProject.opSystems["ALL"]
           
        # create binary project folder
        binaryProjectFolder = _binaryFolder + "/" + _targetProject.binarySubfolder
        os.path.exists(binaryProjectFolder) or os.makedirs(binaryProjectFolder)
    
        # create Win32Header
        if( _targetProject.type != "executable" and _targetProject.GetGenerateWin32Header() ):
            self.__GenerateWin32Header(_targetProject, _binaryFolder)
            if not binaryProjectFolder in opSysAll.public.includeFolders:
                opSysAll.public.includeFolders.append(binaryProjectFolder)
        
        # open cmakelists.txt
        fileCMakeLists = "%s/%s" % (_binaryFolder, _targetProject.cmakeListsSubpath)
        f = open(fileCMakeLists, 'w')
        
        # write header and some cmake fields
        f.write( "# CMakeLists.txt generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        
        f.write( "PROJECT(%s)\n" % (_targetProject.name) )
        f.write( "SET( BINARY_DIR \"%s\")\n" % (_binaryFolder) )
        
        binaryBinFolder = "%s/bin/%s" % (_binaryFolder, _targetProject.installSubFolder)
        
        f.write( "\n# All binary outputs are written to the same folder.\n" )
        f.write( "SET( CMAKE_SUPPRESS_REGENERATION TRUE )\n" )
        f.write( "SET( EXECUTABLE_OUTPUT_PATH \"%s\")\n" % (binaryBinFolder) )
        f.write( "SET( LIBRARY_OUTPUT_PATH \"%s\")\n" % (binaryBinFolder) )
    
        # create config and use files, and include them
        _targetProject.GenerateConfigFile( _binaryFolder)
        _targetProject.GenerateUseFile(_binaryFolder)
        
        # get related projects to be 'used' in the sense of including the use and config file.
        projectsToUse = _targetProject.GetProjectsToUse()
        
        # find and use related projects
        for project in projectsToUse:
          # include config and use file
            f.write( "\n# use %s\n" % (project.name) )
            f.write( "INCLUDE(\"%s\")\n" % (project.GetPathToConfigFile(_binaryFolder)) )
            f.write( "INCLUDE(\"%s\")\n" % (project.GetPathToUseFile(_binaryFolder)) )

        # generate moc files
        cmakeMocInputVar = ""
        if( len(_targetProject.sourcesToBeMoced) ):
            cmakeMocInputVarName = "MOC_%s" % (_targetProject.name)
            cmakeMocInputVar = "${%s}" % (cmakeMocInputVarName)
            f.write("\nQT_WRAP_CPP( %s %s %s )\n" % (_targetProject.name, cmakeMocInputVarName, csnUtility.Join(_targetProject.sourcesToBeMoced, _addQuotes = 1)) )
            
        # generate ui files
        cmakeUIHInputVar = ""
        cmakeUICppInputVar = ""
        if( len(_targetProject.sourcesToBeUIed) ):
            cmakeUIHInputVarName = "UI_H_%s" % (_targetProject.name)
            cmakeUIHInputVar = "${%s}" % (cmakeUIHInputVarName)
            cmakeUICppInputVarName = "UI_CPP_%s" % (_targetProject.name)
            cmakeUICppInputVar = "${%s}" % (cmakeUICppInputVarName)
            f.write("\nQT_WRAP_UI( %s %s %s %s )\n" % (_targetProject.name, cmakeUIHInputVarName, cmakeUICppInputVarName, csnUtility.Join(_targetProject.sourcesToBeUIed, _addQuotes = 1)) )
            
        # write section that is specific for the project type        
        if( len(_targetProject.sources) ):
            f.write( "\n# Add target\n" )
            
            # add definitions
            for opSysName in ["WIN32", "NOT WIN32"]:
                opSys = _targetProject.opSystems[opSysName]
                if( len(opSys.private.definitions) ):
                    f.write( "IF(%s)\n" % (opSysName))
                    f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(opSys.private.definitions) )
                    f.write( "ENDIF(%s)\n" % (opSysName))
            if( len(opSysAll.private.definitions) ):
                f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(opSysAll.private.definitions) )
            
            # add sources
            if(_targetProject.type == "executable" ):
                f.write( "ADD_EXECUTABLE(%s %s %s %s %s)\n" % (_targetProject.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(_targetProject.sources, _addQuotes = 1)) )
                
            elif(_targetProject.type == "library" ):
                f.write( "ADD_LIBRARY(%s STATIC %s %s %s %s)\n" % (_targetProject.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(_targetProject.sources, _addQuotes = 1)) )
            
            elif(_targetProject.type == "dll" ):
                f.write( "ADD_LIBRARY(%s SHARED %s %s %s %s)\n" % (_targetProject.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(_targetProject.sources, _addQuotes = 1)) )
                
            else:
                raise NameError, "Unknown project type %s" % _targetProject.type

            # write section for sorting moc and ui files in a separate folder in Visual Studio
            f.write( "\n # Create source groups \n" )
            f.write( "IF (WIN32)\n" )
            f.write( "  SOURCE_GROUP(\"Generated MOC Files\" REGULAR_EXPRESSION moc_[a-zA-Z0-9_]*[.]cxx$)\n")
            f.write( "  SOURCE_GROUP(\"Forms\" REGULAR_EXPRESSION [.]ui$)\n")
            f.write( "ENDIF(WIN32)\n\n" )
            
            # add standard definition to allow multiply defined symbols in the linker
            f.write( "SET_TARGET_PROPERTIES(%s PROPERTIES LINK_FLAGS \"/FORCE:MULTIPLE\")" % _targetProject.name)
            
            # add install rule
            if( _installFolder != "" and _targetProject.type != "library"):
                destination = "%s/%s" % (_installFolder, _targetProject.installSubFolder)
                f.write( "\n# Rule for installing files in location %s\n" % destination)
                f.write( "INSTALL(TARGETS %s DESTINATION %s)\n" % (_targetProject.name, destination) )
                
        # Find projects that must be generated. A separate list is used to ease debugging.
        projectsToGenerate = set()
        requiredProjects = _targetProject.RequiredProjects(_recursive = 1)        
        for projectToGenerate in requiredProjects:
            # determine if we must Generate the project. If a required project will generate it, 
            # then leave it to the required project. This will prevent multiple generation of the same project.
            # If a non-required project will generate it, then still generate the project 
            # (the non-required project may depend on target project to generate project, creating a race condition).
            generateProject = not projectToGenerate in _generatedList and projectToGenerate.type != "third party"
            if( generateProject ):
                for requiredProject in _targetProject.RequiredProjects(_recursive = 0):
                    if( requiredProject.DependsOn(projectToGenerate) ):
                        generateProject = 0
            if( generateProject ):
                projectsToGenerate.add(projectToGenerate)
        f.write( "\n" )
        
        # add non-required projects that have not yet been generated to projectsToGenerate
        for project in _targetProject.projectsNonRequired:
            if( not project in _generatedList ):
                projectsToGenerate.add(project)

        # generate projects, and add a line with ADD_SUBDIRECTORY
        for project in projectsToGenerate:
            # check again if a previous iteration of this loop didn't add project to the generated list
            if not project in _generatedList:
                f.write( "ADD_SUBDIRECTORY(\"${BINARY_DIR}/%s\" \"${BINARY_DIR}/%s\")\n" % (project.binarySubfolder, project.binarySubfolder) )
                self.Generate(project, _binaryFolder, _installFolder, _generatedList, _knownProjectNames)
           
        # add dependencies
        f.write( "\n" )
        for project in requiredProjects:
            if( len(project.sources) ):
                f.write( "ADD_DEPENDENCIES(%s %s)\n" % (_targetProject.name, project.name) )
        
        # if top level project, add install rules for all the filesToInstall
        if isTopLevelProject:
            for mode in ("debug", "release"):
                for project in _targetProject.GetProjectsToUse():
                    # iterate over filesToInstall to be copied in this mode
                    for location in project.filesToInstall[mode].keys():
                        files = ""
                        for file in project.filesToInstall[mode][location]:
                            files += "%s " % file.replace("\\", "/")
                        if files != "":
                            destination = "%s/%s" % (_installFolder, location)
                            f.write( "\n# Rule for installing files in location %s\n" % destination)
                            f.write("INSTALL(FILES %s DESTINATION %s CONFIGURATIONS %s)\n" % (files, destination, mode.upper()))
                        
        f.close()

    def PostProcess(self, _targetProject, _binaryFolder):
        """
        Apply post-processing after the CMake generation for _targetProject and all its child projects.
        """
        self.PostProcessOneProject(_targetProject, _binaryFolder)
        for project in _targetProject.projects:
            self.PostProcessOneProject(project, _binaryFolder)
        
    def PostProcessOneProject(self, _project, _binaryFolder):
        """
        Apply post-processing after the CMake generation only for _project (not its children).
        """
        binaryProjectFolder = _binaryFolder + "/" + _project.binarySubfolder
        # vc proj to patch
        vcprojFilename = "%s/%s.vcproj" % (binaryProjectFolder, _project.name)

        # if there is a vcproj, and we want a precompiled header
        if _project.precompiledHeader != "" and os.path.exists(vcprojFilename):
            # binary pch file to generate
            pchFilename = "%s/%s.pch" % (binaryProjectFolder, _project.name)
            # this is the name of the cpp file that will build the precompiled headers
            pchCppFilename = "%sPCH.cpp" % (_project.name)

            # patch the vcproj            
            f = open(vcprojFilename, 'r')
            vcproj = f.read()
            f.close()
            vcprojOrg = vcproj 
            
            # add project pch settings
            searchString = "RuntimeTypeInfo=\"TRUE\"\n"
            replaceString = """RuntimeTypeInfo="TRUE"
UsePrecompiledHeader="3"
PrecompiledHeaderThrough="%s" 
PrecompiledHeaderFile="%s"
""" % (_project.precompiledHeader, pchFilename)
            vcproj = vcproj.replace(searchString, replaceString)
            
            # add pchCpp to the solution
            searchString = "<Files>\n"
            replaceString = """
    <Files>
		<Filter
			Name="PCH Files"
			Filter="">
			<File
				RelativePath="%s">
				<FileConfiguration
					Name="Debug|Win32">
					<Tool
						Name="VCCLCompilerTool"
						UsePrecompiledHeader="1"/>
				</FileConfiguration>
				<FileConfiguration
					Name="Release|Win32">
					<Tool
						Name="VCCLCompilerTool"
						UsePrecompiledHeader="1"/>
				</FileConfiguration>
			</File>
		</Filter>
""" % pchCppFilename             
            vcproj = vcproj.replace(searchString, replaceString)
            
            # force include of the pch header file
            searchString = "CompileAs=\"2\"\n"
            replaceString = """CompileAs="2"
ForcedIncludeFiles="%s"
""" % _project.precompiledHeader
            vcproj = vcproj.replace(searchString, replaceString)

            # create file pchCppFilename
            f = open("%s/pchCppFilename" % binaryProjectFolder, 'w')
            f.write("// Automatically generated file for builing the precompiled headers file. DO NOT EDIT\n")
            f.write("#include \"%s\"" % _project.precompiledHeader) 
            f.close()
            
            # write patched vcproj
            f = open(vcprojFilename, 'w')
            f.write(vcproj)
            f.close()
    
    def __GenerateWin32Header(self, _targetProject, _binaryFolder):
        """
        Generates the ProjectNameWin32.h header file for exporting/importing dll functions.
        """
        templateFilename = root + "/CSnake/TemplateSourceFiles/Win32Header.h"
        if( _targetProject.type == "library" ):
            templateFilename = root + "/CSnake/TemplateSourceFiles/Win32Header.lib.h"
        templateOutputFilename = "%s/%s/%sWin32Header.h" % (_binaryFolder, _targetProject.binarySubfolder, _targetProject.name)
        
        assert os.path.exists(templateFilename), "File not found %s\n" % (templateFilename)
        f = open(templateFilename, 'r')
        template = f.read()
        template = template.replace('${PROJECTNAME_UPPERCASE}', _targetProject.name.upper())
        template = template.replace('${PROJECTNAME}', _targetProject.name)
        f.close()
        
        # don't overwrite the existing file if it contains the same text, because this will trigger a source recompile later!
        if( csnUtility.FileToString(templateOutputFilename) != template ):
            f = open(templateOutputFilename, 'w')
            f.write(template)
            f.close()
        
class Project:
    """
    Contains the data for the makefile (or vcproj) for a project.
    _name -- Name of the project, e.g. \"SampleApp\"
    _type -- Type of the project, should be \"executable\", \"library\", \"dll\" or \"third party\"
    _callerDepth - This (advanced) parameter determines who is calling the constructor. The name of the caller is used
    to fill the value of self.sourceRootFolder. Normally, you don't need to change this parameter.

    Config and use file:
    CMake uses config and use files to let packages use other packages. The config file assigns a number of variables
    such as SAMPLE_APP_INCLUDE_DIRECTORIES and SAMPLE_APP_LIBRARY_DIRECTORIES. The use file uses these values to add
    include directories and library directories to the current CMake target. The standard way to use these files is to a)
    make sure that SAMPLE_APP_DIR points to the location of SAMPLE_APPConfig.cmake and UseSAMPLE_APP.cmake, b) 
    call FIND_PACKAGE(SAMPLE_APP) and c) call INCLUDE(${SAMPLE_APP_USE_FILE}. In step b) the config file of SAMPLE_APP is included and
    in step c) the necessary include directories, library directories etc are added to the current target.
    To adhere to normal CMake procedures, csnBuild also uses the use file and config file. However, FIND_PACKAGE is not needed,
    because we can directly include first the config file and then the use file.
    
    The constructors initialises these member variables:
    self.binarySubfolder -- Direct subfolder - within the binary folder - for this project. Is either 'executable' or 'library'.
    self.installSubfolder -- Direct subfolder - within the install folder - for targets generated by this project.
    self.useBefore -- A list of projects. This project must be used before the projects in this list.
    self.configFilePath -- The config file for the project. See above.
    self.sources -- Sources to be compiled for this target.
    self.opSystems -- Dictionary (WIN32/NOT WIN32/ALL -> OpSys) with definitions to be used for different operating systems. 
    self.sourcesToBeMoced -- Sources for which a moc file must be generated.
    self.sourcesToBeUIed -- Sources for which qt's UI.exe must be run.
    self.filesToInstall -- Contains files to be installed in the binary folder. It has the structure filesToInstall[mode][installPath] = files.
    For example: if self.filesToInstall[\"debug\"][\"data\"] = [\"c:/one.txt\", \"c:/two.txt\"], 
    then c:/one.txt and c:/two.txt must be installed in the data subfolder of the binary folder when in debug mode.
    self.useFilePath -- Path to the use file of the project. If it is relative, then the binary folder will be prepended.
    self.cmakeListsSubpath -- The cmake file that builds the project as a target
    self.projects -- Set of related project instances. These projects have been added to self using AddProjects.
    self.projectsNonRequired -- Subset of self.projects. Contains projects that self doesn't depend on.
    self.generateWin32Header -- Flag that says if a standard Win32Header.h must be generated
    self.precompiledHeader -- Name of the precompiled header file. If non-empty, and using Visual Studio (on Windows),
    then precompiled headers is set up.    
    """
    
    def __init__(self, _name, _type, _callerDepth = 1):
        self.sources = []

        self.opSystems = dict()
        for opSysName in ["WIN32", "NOT WIN32", "ALL"]:
            opSys = OpSys()
            self.opSystems[opSysName] = opSys

        self.precompiledHeader = ""
        self.sourcesToBeMoced = []
        self.sourcesToBeUIed = []
        self.name = _name
        self.filesToInstall = dict()
        self.filesToInstall["debug"] = dict()
        self.filesToInstall["release"] = dict()
        self.type = _type
        self.sourceRootFolder = os.path.normpath(os.path.dirname(Caller(_callerDepth)[0])).replace("\\", "/")
        self.useBefore = []
        if( self.type == "dll" ):
            self.binarySubfolder = "library/%s" % (_name)
        else:
            self.binarySubfolder = "%s/%s" % (self.type, _name)
        self.installSubFolder = ""
        self.configFilePath = "%s/%sConfig.cmake" % (self.binarySubfolder, _name)
        self.useFilePath = "%s/Use%s.cmake" % (self.binarySubfolder, _name)
        self.cmakeListsSubpath = "%s/CMakeLists.txt" % (self.binarySubfolder)
        self.projects = set()
        self.projectsNonRequired = set()
        self.generateWin32Header = 1
        
    def AddProjects(self, _projects, _dependency = 1):
        """ 
        Adds projects in _projects as required projects.
        _dependency - Flag that states that self target requires (is dependent on) _projects.
        Raises StandardError in case of a cyclic dependency.
        """
        for projectToAdd in _projects:
            if( self is projectToAdd ):
                raise DependencyError, "Project %s cannot be added to itself" % (projectToAdd.name)
                
            if( not projectToAdd in self.projects ):
                if( _dependency and projectToAdd.DependsOn(self) ):
                    raise DependencyError, "Circular dependency detected during %s.AddProjects(%s)" % (self.name, projectToAdd.name)
                self.projects.add( projectToAdd )
                if( not _dependency ):
                    self.projectsNonRequired.add( projectToAdd )

    def AddSources(self, _listOfSourceFiles, _moc = 0, _ui = 0, _checkExists = 1):
        """
        Adds items to self.sources. For each source file that is not an absolute path, self.sourceRootFolder is prefixed.
        Entries of _listOfSourceFiles may contain wildcards, such as src/*/*.h.
        If _moc, then a moc file is generated for each header file in _listOfSourceFiles.
        If _ui, then qt's ui.exe is run for the file.
        If _checkExists, then added sources (possibly after wildcard expansion) must exist on the filesystem, or an exception is thrown.
        """
        for sourceFile in _listOfSourceFiles:
            sources = self.Glob(sourceFile)
            if( _checkExists and not len(sources) ):
                raise IOError, "Path file not found %s" % (sourceFile)
            
            for source in sources:
                # csnUtility.Log("Adding %s\n" % (source))
                if _moc and not source in self.sourcesToBeMoced:
                    self.sourcesToBeMoced.append(source)
                
                if( not source in self.sources ):
                    if( _ui ):
                        self.sourcesToBeUIed.append(source)
                    self.sources.append(source)

    def AddFilesToInstall(self, _listOfFiles, _location = '.', _debugOnly = 0, _releaseOnly = 0):
        """
        Adds items to self.filesToInstall.
        Entries of _listOfFiles may contain wildcards, such as lib/*/*.dll.
        Relative paths in _listOfFiles are assumed to be relative to the root of the binary folder where the targets 
        are created.
        _debugOnly - If true, then the dll is only installed to the debug install folder.
        _releaseOnly - If true, then the dll is only installed to the release install folder.
        """
        for dll in _listOfFiles:
            if not _debugOnly:
                if not self.filesToInstall["release"].has_key(_location):
                    self.filesToInstall["release"][_location] = []
                if not dll in self.filesToInstall["release"][_location]:
                    self.filesToInstall["release"][_location].append( dll )
            if not _releaseOnly:
                if not self.filesToInstall["debug"].has_key(_location):
                    self.filesToInstall["debug"][_location] = []
                if not dll in self.filesToInstall["debug"][_location]:
                    self.filesToInstall["debug"][_location].append( dll )
                
    def AddDefinitions(self, _listOfDefinitions, _private = 0, _WIN32 = 0, _NOT_WIN32 = 0 ):
        """
        Adds definitions to self.opSystems. 
        """
        opSystemName = self.__GetOpSysName(_WIN32, _NOT_WIN32)            
        opSys = self.opSystems[opSystemName]
        if( _private ):
            opSys.private.definitions.extend(_listOfDefinitions)
        else:
            opSys.public.definitions.extend(_listOfDefinitions)
        
    def AddPublicIncludeFolders(self, _listOfIncludeFolders):
        """
        Adds items to self.publicIncludeFolders. 
        If an item has a relative path, then it will be prefixed with _sourceRootFolder.
        Added include paths must exist on the filesystem.
        """
        opSysAll = self.opSystems["ALL"]
        for includeFolder in _listOfIncludeFolders:
            opSysAll.public.includeFolders.append( self.__FindPath(includeFolder) )
        
    def SetPrecompiledHeader(self, _precompiledHeader):
        """
        If _precompiledHeader is not "", then precompiled headers are used in Visual Studio (Windows) with
        this filename. 
        """
        globResult = self.Glob(_precompiledHeader)
        assert len(globResult) == 1, "Error locating precompiled header file %s" % _precompiledHeader
        self.precompiledHeader = globResult[0]
        
    def AddPublicLibraryFolders(self, _listOfLibraryFolders):
        """
        Adds items to self.publicLibraryFolders. 
        If an item has a relative path, then it will be prefixed with _sourceRootFolder.
        Added library paths must exist on the filesystem.
        """
        opSysAll = self.opSystems["ALL"]
        for libraryFolder in _listOfLibraryFolders:
            opSysAll.public.libraryFolders.append( self.__FindPath(libraryFolder) )
        
    def AddPublicLibraries(self, _type, _listOfLibraries, _WIN32 = 0, _NOT_WIN32 = 0):
        """
        Adds items to self.publicLibraries. 
        _type - Should be \"debug\", \"optimized\" or \"all\".
        """
        assert _type in ("debug", "optimized", "all"), "%s not any of (\"debug\", \"optimized\", \"all\"" % (_type)
        if( _type == "all" ):
            _type = ""

        opSysName = self.__GetOpSysName(_WIN32, _NOT_WIN32)
        opSys = self.opSystems[opSysName]            
            
        for library in _listOfLibraries:
            opSys.public.libraries.append("%s %s" % (_type, library))
            
    def __GetOpSysName(self, _WIN32, _NOT_WIN32):
        """
        Returns "ALL", "WIN32" or "NOT WIN32" 
        """
        if( _WIN32 and _NOT_WIN32 ):
            _WIN32 = _NOT_WIN32 = 0
        compiler = "ALL"
        if( _WIN32 ):
            compiler = "WIN32"
        elif( _NOT_WIN32 ):
            compiler = "NOT WIN32"
        return compiler
        
    def __FindPath(self, _path):
        """ 
        Tries to locate _path as an absolute path or as a path relative to self.sourceRootFolder. 
        Returns an absolute path, containing only forward slashes.
        Throws IOError if path was not found.
        """
        # csnUtility.Log( "Finding %s in %s\n" % (_path, self.sourceRootFolder) )
        
        path = _path
        if( not os.path.isabs(path) ):
            path = os.path.abspath("%s/%s" % (self.sourceRootFolder, path))
        if( not os.path.exists(path) ):
            raise IOError, "Path file not found %s (tried %s)" % (_path, path)
            
        path = path.replace("\\", "/")
        assert not csnUtility.HasBackSlash(path), path
        return path
        
    def Glob(self, _path):
        """ 
        Returns a list of files that match _path (which can be absolute, or relative to self.sourceRootFolder). 
        The return paths are absolute, containing only forward slashes.
        """
        path = _path
        if not os.path.isabs(_path):
            path = os.path.abspath("%s/%s" % (self.sourceRootFolder, path))
        return [x.replace("\\", "/") for x in glob.glob(path)]
    
    def DependsOn(self, _otherProject, _skipList = None):
        """ 
        Returns true if self is (directly or indirectly) dependent upon _otherProject. 
        _skipList - Used to not process project twice during the recursion (also prevents infinite loops).
        """
        if _skipList is None:
            _skipList = []
        
        assert not self in _skipList, "%s should not be in stoplist" % (self.name)
        _skipList.append(self)
        
        for requiredProject in self.RequiredProjects():
            if requiredProject in _skipList:
                continue
            if requiredProject is _otherProject or requiredProject.DependsOn(_otherProject, _skipList ):
                return 1
        return 0
        
    def RequiredProjects(self, _recursive = 0):
        """
        Return a set of projects that self depends upon.
        If recursive is true, then required projects of required projects are also retrieved.
        """
        result = self.projects - self.projectsNonRequired
        if( _recursive ):
            moreResults = set()
            for project in result:
                moreResults.update( project.RequiredProjects(_recursive) )
            result.update(moreResults)
        return result
        
    def UseBefore(self, _otherProject):
        """ 
        Indicate that self must be used before _otherProjects in a cmake file. 
        Throws DependencyError if _otherProject wants to be used before self.
        """
        if( _otherProject.WantsToBeUsedBefore(self) ):
            raise DependencyError, "Cyclic use-before relation between %s and %s" % (self.name, _otherProject.name)
        self.useBefore.append(_otherProject)
        
    def WantsToBeUsedBefore(self, _otherProject):
        """ 
        Return true if self wants to be used before _otherProject.
        """
        if( self is _otherProject ):
            return 0
            
        if( _otherProject in self.useBefore ):
            return 1
            
        for requiredProject in self.RequiredProjects(1):
            if( _otherProject in requiredProject.useBefore ):
                return 1
                
        return 0
           
    def GetProjectsToUse(self):
        """
        Determine a list of projects that must be used (meaning: include the config and use file) to generate this project.
        Note that self is also included in this list.
        The list is sorted in the correct order, using Project.WantsToBeUsedBefore.
        """
        result = []
        
        projectsToUse = [project for project in self.RequiredProjects(_recursive = 1)]
        assert not self in projectsToUse, "%s should not be in projectsToUse" % (self.name)
        projectsToUse.append(self)
        
        (count, maxCount) = (0, 1)
        for i in range(len(projectsToUse)):
            maxCount = maxCount * (i+1)
        
        while (len(projectsToUse)):
            assert count < maxCount
            count += 1
            project = projectsToUse.pop()

            # check if we must skip this project for now, because another project must be used before this one
            skipThisProjectForNow = 0
            for otherProject in projectsToUse:
                if( otherProject.WantsToBeUsedBefore(project) ):
                    #print ("%s wants to be before %s\n" % (otherProject.name, project.name))
                    skipThisProjectForNow = 1
            if( skipThisProjectForNow ):
                projectsToUse.insert(0, project)
                continue
            else:
                result.append(project)
          
        return result
        
    def GenerateConfigFile(self, _binaryFolder):
        """
        Generates the XXXConfig.cmake file for this project.
        """
        fileConfig = "%s/%s" % (_binaryFolder, self.configFilePath)
        f = open(fileConfig, 'w')
        
        opSysAll = self.opSystems["ALL"]
        
        # write header and some cmake fields
        f.write( "# File generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "SET( %s_FOUND \"TRUE\" )\n" % (self.name) )
        f.write( "SET( %s_INCLUDE_DIRS %s )\n" % (self.name, csnUtility.Join(opSysAll.public.includeFolders, _addQuotes = 1)) )
        f.write( "SET( %s_LIBRARY_DIRS %s )\n" % (self.name, csnUtility.Join(opSysAll.public.libraryFolders, _addQuotes = 1)) )
        for opSysName in ["WIN32", "NOT WIN32"]:
            opSys = self.opSystems[opSysName]
            if( len(opSys.public.libraries) ):
                f.write( "IF(%s)\n" % (opSysName))
                f.write( "SET( %s_LIBRARIES %s )\n" % (self.name, csnUtility.Join(opSys.public.libraries, _addQuotes = 1)) )
                f.write( "ENDIF(%s)\n" % (opSysName))
        opSysAll = self.opSystems["ALL"]
        if( len(opSysAll.public.libraries) ):
            f.write( "SET( %s_LIBRARIES ${%s_LIBRARIES} %s )\n" % (self.name, self.name, csnUtility.Join(opSysAll.public.libraries, _addQuotes = 1)) )

    def GenerateUseFile(self, _binaryFolder):
        """
        Generates the UseXXX.cmake file for this project.
        """
        fileUse = "%s/%s" % (_binaryFolder, self.useFilePath)
        f = open(fileUse, 'w')
        
        # write header and some cmake fields
        f.write( "# File generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "INCLUDE_DIRECTORIES(${%s_INCLUDE_DIRS})\n" % (self.name) )
        f.write( "LINK_DIRECTORIES(${%s_LIBRARY_DIRS})\n" % (self.name) )
        f.write( "LINK_LIBRARIES(${%s_LIBRARIES})\n" % (self.name) )

        # write definitions     
        for opSysName in ["WIN32", "NOT WIN32"]:
            opSys = self.opSystems[opSysName]
            if( len(opSys.public.definitions) ):
                f.write( "IF(%s)\n" % (opSysName))
                f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(opSys.public.definitions) )
                f.write( "ENDIF(%s)\n" % (opSysName))
        opSysAll = self.opSystems["ALL"]
        if( len(opSysAll.public.definitions) ):
            f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(opSysAll.public.definitions) )
   
        # write definitions that state whether this is a static library
        #if self.type == "library":
        #    f.write( "ADD_DEFINITIONS(%sSTATIC)\n" % self.name )
            
    def GetPathToConfigFile(self, _binaryFolder):
        """ 
        Returns self.useFilePath if it is absolute. Otherwise, returns _binaryFolder + self.useFilePath.
        """
        if( os.path.isabs(self.configFilePath) ):
            return self.configFilePath
        else:
            return "%s/%s" % (_binaryFolder, self.configFilePath)

    def GetPathToUseFile(self, _binaryFolder):
        """ 
        Returns self.useFilePath if it is absolute. Otherwise, returns _binaryFolder + self.useFilePath.
        """
        if( os.path.isabs(self.useFilePath) ):
            return self.useFilePath
        else:
            return "%s/%s" % (_binaryFolder, self.useFilePath)
        
    def ResolvePathsOfFilesToInstall(self, _thirdPartyBinFolder):
        """ This function replaces relative paths and wildcards in self.filesToInstall with absolute paths without wildcards. """
        for mode in ("debug", "release"):
            for project in self.GetProjectsToUse():
                for location in project.filesToInstall[mode].keys():
                    newList = []
                    for dllPattern in project.filesToInstall[mode][location]:
                        path = dllPattern.replace("\\", "/")
                        if not os.path.isabs(path):
                            path = "%s/%s" % (_thirdPartyBinFolder, path)
                        for dll in glob.glob(path):
                            newList.append(dll)
                    project.filesToInstall[mode][location] = newList
    
    def SetGenerateWin32Header(self, _flag):
        self.generateWin32Header = _flag

    def GetGenerateWin32Header(self):
        return self.generateWin32Header
           