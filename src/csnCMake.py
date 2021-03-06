## @package csnCMake
# Definition of the Writer class. 
import csnUtility
import os
import csnProject

def Quote(string):
    return '"%s"' % string.replace('"', '\\"')

class Writer:
    """ Class responsible for writing the CMake related files."""
    def __init__(self, _project):
        self.project = _project
        self.tmpCMakeListsFile = self.project.GetCMakeListsFilename() + ".tmp"
        
    def __OpenFile(self):
        self.file = open(self.tmpCMakeListsFile, 'w')
        
    def __WriteHeader(self):
        """ Write header and some cmake fields. """
        
        self.file.write( "# CMakeLists.txt generated automatically by the CSnake generator.\n" )
        self.file.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        self.file.write( "PROJECT(%s)\n" % (self.project.name) )
        self.file.write( "SET( BINARY_DIR \"%s\")\n" % (self.project.context.GetOutputFolder(self.project.context.GetConfigurationName())) )
        self.file.write( "MESSAGE( STATUS \"Processing %s\" )\n" % self.project.name )

        if not self.project.context.GetConfigurationName() == "DebugAndRelease":
            self.file.write( "SET( CMAKE_BUILD_TYPE %s )\n" % (self.project.context.GetConfigurationName()) )
        
        self.file.write( "\n# All binary outputs are written to the same folder.\n" )
        self.file.write( "SET( CMAKE_SUPPRESS_REGENERATION TRUE )\n" )
        self.file.write( "SET( EXECUTABLE_OUTPUT_PATH \"%s\")\n" % self.project.GetBuildResultsFolder(self.project.context.GetConfigurationName()) )
        self.file.write( "SET( LIBRARY_OUTPUT_PATH \"%s\")\n" % self.project.GetBuildResultsFolder(self.project.context.GetConfigurationName()) )

        # Forced for CMake 2.8
        self.file.write( "cmake_minimum_required(VERSION 2.4.6)\n\n" )
        
        # Adding two types of libraries (with full path or just the name)
        self.file.write( "if(COMMAND cmake_policy)\n" )
        self.file.write( "  cmake_policy(SET CMP0003 NEW)\n" )
        self.file.write( "endif(COMMAND cmake_policy)\n\n" )

    def __WriteCommandsToGenerate(self, projectsToGenerate):
        self.file.write( "\n" )
        for projectToGenerate in projectsToGenerate:
            includeInSolution = projectToGenerate in self.project.dependenciesManager.projectsIncludedInSolution
            if includeInSolution:
                self.file.write( "ADD_SUBDIRECTORY(\"%s\" \"%s\")\n" % (projectToGenerate.GetBuildFolder(), projectToGenerate.GetBuildFolder()) )
        self.file.write( "\n" )
    
    def __WriteDependencyCommands(self, dependencyProjects):
        self.file.write( "\n" )
        for dependencyProject in dependencyProjects:
            staticLibUsingAnotherLib = self.project.type == "library" and dependencyProject.type != "executable" 
            noSources = (not isinstance(dependencyProject, csnProject.GenericProject)) or len(dependencyProject.GetSources()) == 0 
            if (csnUtility.IsWindowsPlatform() and staticLibUsingAnotherLib) or noSources: 
                continue
            else:
                self.file.write( "ADD_DEPENDENCIES(%s %s)\n" % (self.project.name, dependencyProject.name) )
    
    def __WriteInstallCommands(self):
        for mode in ("Debug", "Release"):
            for project in self.project.dependenciesManager.ProjectsToUse():
                # iterate over filesToInstallResolved to be copied in this mode
                for location, filesToInstall in project.installManager.filesToInstallResolved[mode].iteritems():
                    if len(filesToInstall):
                        filesToInstall = map(csnUtility.NormalizePath, filesToInstall)
                        filesToInstall = map(Quote, filesToInstall)
                        filesToInstallList = "\n    ".join(filesToInstall)
                        destination = "%s/%s" % (self.project.context.GetInstallFolder(), location)
                        self.file.write( "\n# Rule for installing files in location %s\n" % destination)
                        self.file.write("INSTALL(FILES %s\n    DESTINATION \"%s\"\n    CONFIGURATIONS %s)\n"
                                % (filesToInstallList, destination, mode.upper()))
    
    def __CreateCMakeSection_IncludeConfigAndUseFiles(self):
        """ Include the use file and config file for any dependency project, and finally also
        add the use and config file for this project (do this last, so that all definitions from
        the dependency projects are already included).
        """
        for project in self.project.dependenciesManager.ProjectsToUse():
            includeInSolution = project in self.project.dependenciesManager.projectsIncludedInSolution
            public = (self.project.name != project.name and ( not csnUtility.IsWindowsPlatform() or not includeInSolution ) )
            self.file.write( "INCLUDE(\"%s\")\n" % (project.pathsManager.GetPathToConfigFile(public) ))
            self.file.write( "INCLUDE(\"%s\")\n" % (project.pathsManager.GetPathToUseFile()) )
    
    def __CreateCMakeSection_SourceGroups(self):
        """ Create source groups in the CMakeLists.txt """
        for groupName in self.project.GetCompileManager().sourceGroups:
            self.file.write( "\n # Create %s group \n" % groupName )
            self.file.write( "IF (WIN32)\n" )
            self.file.write( "  SOURCE_GROUP(\"%s\" FILES %s)\n" % (groupName, csnUtility.Join(self.project.GetCompileManager().sourceGroups[groupName], _addQuotes = 1)))
            self.file.write( "ENDIF(WIN32)\n\n" )
    
    def __CreateCMakeSection_MocRules(self):
        """ Create moc rules in the CMakeLists.txt """
        cmakeMocInputVar = ""
        if len(self.project.GetCompileManager().sourcesToBeMoced):
            cmakeMocInputVarName = "MOC_%s" % (self.project.name)
            cmakeMocInputVar = "${%s}" % (cmakeMocInputVarName)
            self.file.write("\nQT_WRAP_CPP( %s %s %s )\n" % (self.project.name, cmakeMocInputVarName, csnUtility.Join(self.project.GetCompileManager().sourcesToBeMoced, _addQuotes = 1)) )
            # write section for sorting moc files in a separate folder in Visual Studio
            self.file.write( "\n # Create MOC group \n" )
            self.file.write( "IF (WIN32)\n" )
            self.file.write( "  SOURCE_GROUP(\"Generated MOC Files\" REGULAR_EXPRESSION moc_[a-zA-Z0-9_]*[.]cxx$)\n")
            self.file.write( "ENDIF(WIN32)\n\n" )
        return cmakeMocInputVar
    
    def __CreateCMakeSection_UicRules(self):
        """ Create uic rules in the CMakeLists.txt """
        cmakeUIHInputVar = ""
        cmakeUICppInputVar = ""
        if len(self.project.GetCompileManager().sourcesToBeUIed):
            cmakeUIHInputVarName = "UI_H_%s" % (self.project.name)
            cmakeUIHInputVar = "${%s}" % (cmakeUIHInputVarName)
            cmakeUICppInputVarName = "UI_CPP_%s" % (self.project.name)
            cmakeUICppInputVar = "${%s}" % (cmakeUICppInputVarName)
            self.file.write("\nQT_WRAP_UI( %s %s %s %s )\n" % (self.project.name, cmakeUIHInputVarName, cmakeUICppInputVarName, csnUtility.Join(self.project.GetCompileManager().sourcesToBeUIed, _addQuotes = 1)) )
            # write section for sorting ui files in a separate folder in Visual Studio
            self.file.write( "\n # Create UI group \n" )
            self.file.write( "IF (WIN32)\n" )
            self.file.write( "  SOURCE_GROUP(\"Forms\" REGULAR_EXPRESSION [.]ui$)\n")
            self.file.write( "ENDIF(WIN32)\n\n" )
        return (cmakeUIHInputVar, cmakeUICppInputVar)
    
    def __CreateCMakeSection_Definitions(self):
        """ Create definitions in the CMakeLists.txt """
        if len(self.project.GetCompileManager().private.definitions):
            self.file.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(self.project.GetCompileManager().private.definitions) )

    def __HasCompilableFiles(self):
        extensions = ["." + x for x in csnUtility.GetSourceFileExtensions()]
        files = filter(lambda x: os.path.splitext(x)[1] in extensions, self.project.GetSources())
        return len( files ) > 0
        
    def __CreateCMakeSection_Sources(self, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar):
        """ Add sources to the target in the CMakeLists.txt """
        sources = self.project.GetSources()
        if not self.__HasCompilableFiles():
            sources.append( csnUtility.GetDummyCppFilename() )
        if self.project.type == "executable":
            self.file.write( "ADD_EXECUTABLE(%s %s %s %s %s)\n" % (self.project.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(sources, _addQuotes = 1)) )
            
        elif self.project.type == "library":
            self.file.write( "ADD_LIBRARY(%s STATIC %s %s %s %s)\n" % (self.project.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(sources, _addQuotes = 1)) )
        
        elif self.project.type == "dll":
            self.file.write( "ADD_LIBRARY(%s SHARED %s %s %s %s)\n" % (self.project.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(sources, _addQuotes = 1)) )

        elif self.project.type == "container":
            self.file.write( "# Container project\n" )
            
        else:
            raise NameError, "Unknown project type %s" % self.project.type
        
    def __CreateCMakeSection_InstallRules(self):
        """ Create install rules in the CMakeLists.txt """
        if self.project.context.GetInstallFolder() != "" and self.project.type != "library":
            destination = "%s/%s" % (self.project.context.GetInstallFolder(), self.project.installSubFolder)
            self.file.write( "\n# Rule for installing files in location %s\n" % destination)
            self.file.write( "INSTALL(TARGETS %s DESTINATION \"%s\")\n" % (self.project.name, destination) )
    
    def __CreateCMakeSection_Rules(self):
        """ Create other rules in the CMakeLists.txt """
        for description, rule in self.project.rules.iteritems():
            self.file.write("\n#Adding rule %s\n" % description)
            command = "ADD_CUSTOM_COMMAND("
            command += "OUTPUT \"%s\"" % rule.output
            command += " COMMAND %s" % rule.command
            if len(rule.depends) > 0:
                command += " DEPENDS"
                for depend in rule.depends:
                    command += " %s" % depend
            command += " WORKING_DIRECTORY \"%s\"" % rule.workingDirectory
            command += " COMMENT \"Running rule %s\"" % description
            command += " VERBATIM"
            command += " )" 
            self.file.write(command)

        # Adding specific windows macros
        if csnUtility.IsWindowsPlatform():
            self.file.write("\n#Adding specific windows macros\n")
            self.file.write("INCLUDE( %s )\n" % "\"%s/cmakeMacros/PlatformDependent.cmake\"" % csnProject.globalCurrentContext.GetThirdPartyFolder( 0 ) )
            self.file.write("INCREASE_MSVC_HEAP_LIMIT( 1000 )\n")
            self.file.write("SUPPRESS_VC8_DEPRECATED_WARNINGS( )\n")
            self.file.write("SUPPRESS_LINKER_WARNING_4089( %s )\n" % self.project.name )
            self.file.write("SUPPRESS_COMPILER_WARNING_DLL_EXPORT( %s )\n" % self.project.name )
            
    
    def __CreateCMakeSection_Link(self):
        """ Create link commands in the CMakeLists.txt """
        if self.project.type in ("dll", "executable"):
            # if the name of the project is self, use libraries to include the ones
            # added using AddLibraries( )
            targetLinkLibraries = ("${%s_LIBRARIES} " % self.project.name)
            for project in self.project.GetProjects(_recursive = 1, _onlyRequiredProjects = 1, _includeSelf=0):
                if not project.type in ("dll", "library", "executable", "prebuilt"):
                    continue
                targetLinkLibraries = (" %s " % project.name) + targetLinkLibraries
            self.file.write( "TARGET_LINK_LIBRARIES(%s %s)\n" % (self.project.name, targetLinkLibraries) )

    def __CreateCMakePrecompiledHeaderPre(self):
        if self.project.GetCompileManager().precompiledHeader != "":
            self.file.write("\n#Adding CMake PrecompiledHeader Pre\n")
            self.file.write("INCLUDE( %s )\n" % "\"%s/cmakeMacros/PCHSupport_26.cmake\"" % csnProject.globalCurrentContext.GetThirdPartyFolder( 0 ) )
            self.file.write("GET_NATIVE_PRECOMPILED_HEADER(\"%s\" \"%s\")\n" % (self.project.name, self.project.GetCompileManager().precompiledHeader) )
            
            #Add precompiled header to sources. This file is generated for windows only 
            # after executing CMake, so it doens't exists at the begining
            if not self.project.context.GetCompiler().IsForPlatform(_WIN32 = 1, _NOT_WIN32 = 0):
                return
            precompiledHeaderCxx = "%s/%s_pch.cxx" % (self.project.GetBuildFolder(),self.project.name)
            self.project.AddSources([precompiledHeaderCxx], _sourceGroup = "PCH Files", _checkExists = 0, _forceAdd = 1)
        
    def __CreateCMakePrecompiledHeaderPost(self):
        if self.project.GetCompileManager().precompiledHeader != "":
            self.file.write("\n#Adding CMake PrecompiledHeader Post\n")
            self.file.write("ADD_NATIVE_PRECOMPILED_HEADER(\"%s\" \"%s\")\n" % (self.project.name, self.project.GetCompileManager().precompiledHeader) )

    def __CreateCMakeSections(self):
        """ Writes different CMake sections for this project to the file f. """
    
        self.__CreateCMakeSection_IncludeConfigAndUseFiles()

        self.project.CMakeInsertBeforeTarget( self.file )
        
        self.__CreateCMakePrecompiledHeaderPre()
        self.__CreateCMakeSection_SourceGroups()
        cmakeMocInputVar = self.__CreateCMakeSection_MocRules()
        (cmakeUIHInputVar, cmakeUICppInputVar) = self.__CreateCMakeSection_UicRules()
            
        # write section that is specific for the project type   
        self.file.write( "\n# Add target\n" )
        self.__CreateCMakeSection_Sources(cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar)
        self.__CreateCMakeSection_Link()
        self.__CreateCMakeSection_Definitions()
        self.__CreateCMakeSection_InstallRules()
        self.__CreateCMakeSection_Rules()
        self.__CreateCMakeSection_AddProperties()
        self.__CreateCMakePrecompiledHeaderPost()
        
        self.project.CMakeInsertAfterTarget( self.file )
    
    def __CloseFile(self):
        self.file.close()
        csnUtility.ReplaceDestinationFileIfDifferentAndSaveBackup(self.tmpCMakeListsFile, self.project.GetCMakeListsFilename())

    def GenerateCMakeLists(self, _generatedProjects, _requiredProjects, _writeInstallCommands):
        self.__OpenFile()
        self.__WriteHeader()
        #if _writeInstallCommands:
        #    for project in self.project.GetProjects(_recursive = True, _includeSelf = True):
        #        self.file.write( "SET( AlreadyUsing%s FALSE CACHE BOOL \"Internal helper\" FORCE )\n" % (project.name) )
        #        self.file.write( "SET( AlreadyUsing%sPrivate FALSE CACHE BOOL \"Internal helper\" FORCE )\n" % (project.name) )

        self.project.CMakeInsertBeginning( self.file )
        
        # wxMitkApplications is a container project that just have ADD_SUBDIRECTORY for each application
        self.__WriteCommandsToGenerate(_generatedProjects)
        if self.project.type != "container":
            self.__CreateCMakeSections()
            self.__WriteDependencyCommands(_requiredProjects)
            if _writeInstallCommands:
                self.__WriteInstallCommands()
        self.__CloseFile()
    
    def GenerateConfigFile(self, _public):
        """
        Generates the XXXConfig.cmake file for this project.
        _public - If true, generates a config file that can be used in any cmake file. If false,
        it generates the private config file that is used in the csnake-generated cmake files.
        """
        fileConfig = self.project.pathsManager.GetPathToConfigFile(_public)
        f = open(fileConfig, 'w')
        
        # create list with folder where libraries should be found. Add the folder where all the targets are placed to this list. 
        publicLibraryFolders = self.project.GetCompileManager().public.libraryFolders
        if _public:
            publicLibraryFolders.append(self.project.GetBuildResultsFolder()) 

        # write header and some cmake fields
        f.write( "# File generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "SET( %s_FOUND TRUE )\n" % (self.project.name) )
        f.write( "SET( %s_USE_FILE \"%s\" )\n" % (self.project.name, self.project.pathsManager.GetPathToUseFile() ) )
        f.write( "SET( %s_INCLUDE_DIRS %s )\n" % (self.project.name, csnUtility.Join(self.project.GetCompileManager().public.includeFolders, _addQuotes = 1)) )
        f.write( "SET( %s_LIBRARY_DIRS %s )\n" % (self.project.name, csnUtility.Join(publicLibraryFolders, _addQuotes = 1)) )
        if len(self.project.GetCompileManager().public.libraries):
            libraries = ""
            for buildType in self.project.GetCompileManager().public.libraries.keys():
                typeString = ""
                if buildType != "":
                    typeString = "\"%s\" " % buildType # something like "debug "
                for library in self.project.GetCompileManager().public.libraries[buildType]:
                    libraries += "%s\"%s\"" % (typeString, library)
            f.write( "SET( %s_LIBRARIES ${%s_LIBRARIES} %s )\n" % (self.project.name, self.project.name, libraries) )

        # add the target of this project to the list of libraries that should be linked
        if _public and len(self.project.GetSources()) > 0 and (self.project.type == "library" or self.project.type == "dll"):
            targetName = self.project.name
            f.write( "SET( %s_LIBRARIES ${%s_LIBRARIES} %s )\n" % (self.project.name, self.project.name, csnUtility.Join([targetName], _addQuotes = 1)) )
                
    def GenerateUseFile(self):
        """
        Generates the UseXXX.cmake file for this project.
        """
        fileUse = self.project.pathsManager.GetPathToUseFile()
        f = open(fileUse, 'w')
        
        # write header and some cmake fields
        f.write( "# File generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        #f.write( "MESSAGE(\"Already using %s = ${AlreadyUsing%s}\")\n" % (self.project.name, self.project.name) )
        f.write( "INCLUDE_DIRECTORIES(${%s_INCLUDE_DIRS})\n" % (self.project.name) )
        f.write( "LINK_DIRECTORIES(${%s_LIBRARY_DIRS})\n" % (self.project.name) )
        
        # write definitions     
        if len(self.project.GetCompileManager().public.definitions):
            f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(self.project.GetCompileManager().public.definitions) )
    
    def __CreateCMakeSection_AddProperties(self):
        """ Add properties in the CMakeLists.txt """
        self.file.write("\n#Adding properties\n" )
        for prop in self.project.properties:
            command = "SET_PROPERTY( TARGET %s PROPERTY %s )\n" % ( self.project.name, prop )
            self.file.write( command )
