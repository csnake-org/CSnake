import csnUtility

class Writer:
    def __init__(self, _project):
        self.project = _project
        self.tmpCMakeListsFile = self.project.GetCMakeListsFilename() + ".tmp"
        
    def __OpenFile(self):
        self.file = open(self.tmpCMakeListsFile, 'w')
        
    def __WriteHeader(self):
        # write header and some cmake fields
        self.file.write( "# CMakeLists.txt generated automatically by the CSnake generator.\n" )
        self.file.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        self.file.write( "PROJECT(%s)\n" % (self.project.name) )
        self.file.write( "SET( BINARY_DIR \"%s\")\n" % (self.project.context.GetOutputFolder(self.project.context.configurationName)) )

        if not self.project.context.configurationName == "DebugAndRelease":
            self.file.write( "SET( CMAKE_BUILD_TYPE %s )\n" % (self.project.context.configurationName) )
        
        self.file.write( "\n# All binary outputs are written to the same folder.\n" )
        self.file.write( "SET( CMAKE_SUPPRESS_REGENERATION TRUE )\n" )
        self.file.write( "SET( EXECUTABLE_OUTPUT_PATH \"%s\")\n" % self.project.GetBinaryInstallFolder(self.project.context.configurationName) )
        self.file.write( "SET( LIBRARY_OUTPUT_PATH \"%s\")\n" % self.project.GetBinaryInstallFolder(self.project.context.configurationName) )

    def __WriteCommandsToGenerate(self, projectsToGenerate):
        self.file.write( "\n" )
        for projectToGenerate in projectsToGenerate:
            self.file.write( "ADD_SUBDIRECTORY(\"%s\" \"%s\")\n" % (projectToGenerate.GetBuildFolder(), projectToGenerate.GetBuildFolder()) )
    
    def __WriteDependencyCommands(self, dependencyProjects):
        self.file.write( "\n" )
        for dependencyProject in dependencyProjects:
            staticLibUsingAnotherLib = self.project.type == "library" and dependencyProject.type != "executable" 
            noSources = len(dependencyProject.GetSources()) == 0 
            if (csnUtility.IsRunningOnWindows() and staticLibUsingAnotherLib) or noSources: 
                continue
            else:
                self.file.write( "ADD_DEPENDENCIES(%s %s)\n" % (self.project.name, dependencyProject.name) )
    
    def __WriteInstallCommands(self):
        for mode in ("Debug", "Release"):
            for project in self.project.ProjectsToUse():
                # iterate over filesToInstall to be copied in this mode
                for location in project.installManager.filesToInstall[mode].keys():
                    files = ""
                    for file in project.installManager.filesToInstall[mode][location]:
                        files += "%s " % csnUtility.NormalizePath(file)
                    if files != "":
                        destination = "%s/%s" % (self.project.context.installFolder, location)
                        self.file.write( "\n# Rule for installing files in location %s\n" % destination)
                        self.file.write("INSTALL(FILES %s DESTINATION \"%s\" CONFIGURATIONS %s)\n" % (files, destination, mode.upper()))
    
    def __CreateCMakeSection_IncludeConfigAndUseFiles(self):
        """ Include the use file and config file for any dependency project, and finally also
        add the use and config file for this project (do this last, so that all definitions from
        the dependency projects are already included).
        """
        for project in self.project.ProjectsToUse():
            self.file.write( "\n# use %s\n" % (project.name) )
            self.file.write( "IF( NOT AlreadyUsing%s )\n" % (project.name) )
            self.file.write( "SET( AlreadyUsing%s TRUE CACHE BOOL \"Internal helper\" FORCE )\n" % (project.name) )
            self.file.write( "INCLUDE(\"%s\")\n" % (project.GetPathToConfigFile(_public = (self.project.name != project.name and not csnUtility.IsRunningOnWindows())) ))
            self.file.write( "INCLUDE(\"%s\")\n" % (project.GetPathToUseFile()) )
            self.file.write( "ENDIF( NOT AlreadyUsing%s )\n" % (project.name) )
    
    def __CreateCMakeSection_SourceGroups(self):
        """ Create source groups in the CMakeLists.txt """
        for groupName in self.project.compileManager.sourceGroups:
            self.file.write( "\n # Create %s group \n" % groupName )
            self.file.write( "IF (WIN32)\n" )
            self.file.write( "  SOURCE_GROUP(\"%s\" FILES %s)\n" % (groupName, csnUtility.Join(self.project.compileManager.sourceGroups[groupName], _addQuotes = 1)))
            self.file.write( "ENDIF(WIN32)\n\n" )
    
    def __CreateCMakeSection_MocRules(self):
        """ Create moc rules in the CMakeLists.txt """
        cmakeMocInputVar = ""
        if len(self.project.compileManager.sourcesToBeMoced):
            cmakeMocInputVarName = "MOC_%s" % (self.project.name)
            cmakeMocInputVar = "${%s}" % (cmakeMocInputVarName)
            self.file.write("\nQT_WRAP_CPP( %s %s %s )\n" % (self.project.name, cmakeMocInputVarName, csnUtility.Join(self.project.compileManager.sourcesToBeMoced, _addQuotes = 1)) )
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
        if len(self.project.compileManager.sourcesToBeUIed):
            cmakeUIHInputVarName = "UI_H_%s" % (self.project.name)
            cmakeUIHInputVar = "${%s}" % (cmakeUIHInputVarName)
            cmakeUICppInputVarName = "UI_CPP_%s" % (self.project.name)
            cmakeUICppInputVar = "${%s}" % (cmakeUICppInputVarName)
            self.file.write("\nQT_WRAP_UI( %s %s %s %s )\n" % (self.project.name, cmakeUIHInputVarName, cmakeUICppInputVarName, csnUtility.Join(self.project.compileManager.sourcesToBeUIed, _addQuotes = 1)) )
            # write section for sorting ui files in a separate folder in Visual Studio
            self.file.write( "\n # Create UI group \n" )
            self.file.write( "IF (WIN32)\n" )
            self.file.write( "  SOURCE_GROUP(\"Forms\" REGULAR_EXPRESSION [.]ui$)\n")
            self.file.write( "ENDIF(WIN32)\n\n" )
        return (cmakeUIHInputVar, cmakeUICppInputVar)
    
    def __CreateCMakeSection_Definitions(self):
        """ Create definitions in the CMakeLists.txt """
        if len(self.project.compileManager.private.definitions):
            self.file.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(self.project.compileManager.private.definitions) )

    def __CreateCMakeSection_Sources(self, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar):
        """ Add sources to the target in the CMakeLists.txt """
        sources = self.project.GetSources()
        if len(sources) == 0:
            sources.append( csnUtility.GetDummyCppFilename() )
        if self.project.type == "executable":
            self.file.write( "ADD_EXECUTABLE(%s %s %s %s %s)\n" % (self.project.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(sources, _addQuotes = 1)) )
            
        elif self.project.type == "library":
            self.file.write( "ADD_LIBRARY(%s STATIC %s %s %s %s)\n" % (self.project.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(sources, _addQuotes = 1)) )
        
        elif self.project.type == "dll":
            self.file.write( "ADD_LIBRARY(%s SHARED %s %s %s %s)\n" % (self.project.name, cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar, csnUtility.Join(sources, _addQuotes = 1)) )
            
        else:
            raise NameError, "Unknown project type %s" % self.project.type
        
    def __CreateCMakeSection_InstallRules(self):
        """ Create install rules in the CMakeLists.txt """
        if self.project.context.installFolder != "" and self.project.type != "library":
            destination = "%s/%s" % (self.project.context.installFolder, self.project.installSubFolder)
            self.file.write( "\n# Rule for installing files in location %s\n" % destination)
            self.file.write( "INSTALL(TARGETS %s DESTINATION \"%s\")\n" % (self.project.name, destination) )
    
    def __CreateCMakeSection_Rules(self):
        """ Create other rules in the CMakeLists.txt """
        for description, rule in self.project.rules.iteritems():
            self.file.write("\n#Adding rule %s\n" % description)
            self.file.write("ADD_CUSTOM_COMMAND( TARGET %s PRE_BUILD COMMAND %s WORKING_DIRECTORY \"%s\" COMMENT \"Running rule %s\" VERBATIM )\n" % (self.project.name, rule.command, rule.workingDirectory, description))
    
    def __CreateCMakeSection_Link(self):
        """ Create link commands in the CMakeLists.txt """
        if self.project.type in ("dll", "executable"):
            targetLinkLibraries = ""
            for project in self.project.GetProjects(_recursive = 1, _onlyRequiredProjects = 1):
                if not project.type in ("dll", "library", "executable", "prebuilt"):
                    continue
                targetLinkLibraries = targetLinkLibraries + ("${%s_LIBRARIES} " % project.name) 
            self.file.write( "TARGET_LINK_LIBRARIES(%s %s)\n" % (self.project.name, targetLinkLibraries) )
        
    def __CreateCMakeSections(self):
        """ Writes different CMake sections for this project to the file f. """
    
        self.__CreateCMakeSection_IncludeConfigAndUseFiles()
        self.__CreateCMakeSection_SourceGroups()
        cmakeMocInputVar = self.__CreateCMakeSection_MocRules()
        (cmakeUIHInputVar, cmakeUICppInputVar) = self.__CreateCMakeSection_UicRules()
            
        # write section that is specific for the project type   
        if len(self.project.GetSources()):
            self.file.write( "\n# Add target\n" )
            self.__CreateCMakeSection_Sources(cmakeUIHInputVar, cmakeUICppInputVar, cmakeMocInputVar)
            self.__CreateCMakeSection_Link()
            self.__CreateCMakeSection_Definitions()
            self.__CreateCMakeSection_InstallRules()
            self.__CreateCMakeSection_Rules()
    
    def __CloseFile(self):
        self.file.close()
        csnUtility.ReplaceDestinationFileIfDifferentAndSaveBackup(self.tmpCMakeListsFile, self.project.GetCMakeListsFilename())

    def GenerateCMakeLists(self, _generatedProjects, _requiredProjects, _writeInstallCommands):
        self.__OpenFile()
        self.__WriteHeader()
        if _writeInstallCommands:
            for project in self.project.GetProjects(_recursive = True, _includeSelf = True):
                self.file.write( "SET( AlreadyUsing%s FALSE CACHE BOOL \"Internal helper\" FORCE )\n" % (project.name) )
        self.__CreateCMakeSections()
        self.__WriteCommandsToGenerate(_generatedProjects)
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
        fileConfig = self.project.GetPathToConfigFile(_public)
        f = open(fileConfig, 'w')
        
        # create list with folder where libraries should be found. Add the bin folder where all the
        # targets are placed to this list. 
        publicLibraryFolders = self.project.compileManager.public.libraryFolders
        if _public:
            publicLibraryFolders.append(self.project.GetBinaryInstallFolder()) 

        # write header and some cmake fields
        f.write( "# File generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "SET( %s_FOUND TRUE )\n" % (self.project.name) )
        f.write( "SET( %s_USE_FILE \"%s\" )\n" % (self.project.name, self.project.GetPathToUseFile() ) )
        f.write( "SET( %s_INCLUDE_DIRS %s )\n" % (self.project.name, csnUtility.Join(self.project.compileManager.public.includeFolders, _addQuotes = 1)) )
        f.write( "SET( %s_LIBRARY_DIRS %s )\n" % (self.project.name, csnUtility.Join(publicLibraryFolders, _addQuotes = 1)) )
        if len(self.project.compileManager.public.libraries):
            f.write( "SET( %s_LIBRARIES ${%s_LIBRARIES} %s )\n" % (self.project.name, self.project.name, csnUtility.Join(self.project.compileManager.public.libraries, _addQuotes = 1)) )

        # add the target of this project to the list of libraries that should be linked
        if _public and len(self.project.GetSources()) > 0 and (self.project.type == "library" or self.project.type == "dll"):
            targetName = self.project.name
            f.write( "SET( %s_LIBRARIES ${%s_LIBRARIES} %s )\n" % (self.project.name, self.project.name, csnUtility.Join([targetName], _addQuotes = 1)) )
                
    def GenerateUseFile(self):
        """
        Generates the UseXXX.cmake file for this project.
        """
        fileUse = self.project.GetPathToUseFile()
        f = open(fileUse, 'w')
        
        # write header and some cmake fields
        f.write( "# File generated automatically by the CSnake generator.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        #f.write( "MESSAGE(\"Already using %s = ${AlreadyUsing%s}\")\n" % (self.project.name, self.project.name) )
        f.write( "INCLUDE_DIRECTORIES(${%s_INCLUDE_DIRS})\n" % (self.project.name) )
        f.write( "LINK_DIRECTORIES(${%s_LIBRARY_DIRS})\n" % (self.project.name) )
        
        # write definitions     
        if len(self.project.compileManager.public.definitions):
            f.write( "ADD_DEFINITIONS(%s)\n" % csnUtility.Join(self.project.compileManager.public.definitions) )