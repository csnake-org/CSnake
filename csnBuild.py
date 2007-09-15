from os import makedirs
import os.path
import sys
import re
import glob
import shutil
import traceback

# ToDo:
# - Have public and private child projects (hide the include paths from its clients)
# - Support copying dlls automatically to the "install" folder of the binary folder. This should be a separate option from the GUI.
# - Create GUI
# = Use environment variables to work around the cmake propagation behaviour

root = "%s/.." % (os.path.dirname(__file__))
root = root.replace("\\", "/")
if( not root in sys.path ):
    sys.path.append(root)

def Log(logString):
        f = open("c:\\log.txt", 'a')
        f.write(logString)
        f.close()

def HasBackSlash(_path):
    p = re.compile(r"[^\\]*\\")
    m = p.match( _path )
    return m

def Join(theList):
    """
    Returns a string that contains the items of theList separated by spaces.
    """
    all = ""
    for x in theList:
        all = all + str(x) + " "
    return all

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

class Generator:
    """
    Generates the CMakeLists.txt for a csnBuild.Project.
    """

    def Generate(self, _targetProject, _binaryFolder, _generatedList = None, _knownProjectNames = None):
        """
        Generates the CMakeLists.txt for a csnBuild.Project in _binaryFolder.
        All binaries are placed in _binaryFolder/bin.
        _binaryFolder -- Target location for the cmake files.
        _generatedList -- List of projects for which Generate was already called
        """

        if( _generatedList is None ):
            _generatedList = []

        if( _knownProjectNames is None ):
            _knownProjectNames = []

        if( _targetProject.name in _knownProjectNames):
            raise NameError, "Each project of must have a unique name. Violating project is %s in folder %s\n" % (_targetProject.name, _targetProject.sourceRootFolder)
        else:
        	_knownProjectNames.append(_targetProject.name)
            
        # Log("Generate %s\n" % (_targetProject.name))
        # for project in _generatedList:
        #     Log("Already generated %s\n" % (project.name))
        # Log("---\n")
        
        # trying to Generate a project twice indicates a logical error in the code        
        assert not _targetProject in _generatedList, "Target project name = %s" % (_targetProject.name)
        _generatedList.append(_targetProject)
        
        # check for backward slashes
        if HasBackSlash(_binaryFolder):
            raise SyntaxError, "Error, backslash found in binary folder %s" % _binaryFolder
        
        # create binary project folder
        binaryProjectFolder = _binaryFolder + "/" + _targetProject.binarySubfolder
        os.path.exists(binaryProjectFolder) or os.makedirs(binaryProjectFolder)
        
        # create Win32Header
        if( _targetProject.type != "executable" ):
			self.__GenerateWin32Header(_targetProject, _binaryFolder)
			assert not binaryProjectFolder in _targetProject.publicIncludeFolders
			_targetProject.publicIncludeFolders.append(binaryProjectFolder)
        
        # open cmakelists.txt
        fileCMakeLists = "%s/%s" % (_binaryFolder, _targetProject.cmakeListsSubpath)
        f = open(fileCMakeLists, 'w')
        
        # write header and some cmake fields
        f.write( "# CMakeLists.txt generated automatically by GBuild.py.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        
        f.write( "PROJECT(%s)\n" % (_targetProject.name) )
        f.write( "SET( BINARY_DIR \"%s\")\n" % (_binaryFolder) )
        
        binaryBinFolder = "%s/bin" % (_binaryFolder)
        
        f.write( "\n# All binary outputs are written to the same folder.\n" )
        f.write( "SET( CMAKE_SUPPRESS_REGENERATION TRUE )\n" )
        f.write( "SET( EXECUTABLE_OUTPUT_PATH \"%s\")\n" % (binaryBinFolder) )
        f.write( "SET( LIBRARY_OUTPUT_PATH  \"%s\")\n" % (binaryBinFolder) )
    
        # create config and use files, and include them
        _targetProject.GenerateConfigFile( _binaryFolder)
        _targetProject.GenerateUseFile(_binaryFolder)
        
        # get child projects to be 'used' in the sense of including the use and config file.
        projectsToUse = _targetProject.GetProjectsToUse()
        
        # find and use child projects
        for project in projectsToUse:
          # include config and use file
            f.write( "\n# use %s\n" % (project.name) )
            f.write( "INCLUDE(${BINARY_DIR}/%s)\n" % (project.configFileSubpath) )
            f.write( "INCLUDE(${BINARY_DIR}/%s)\n" % (project.useFileSubpath) )

        # generate moc files
        cmakeMocInputVar = ""
        if( len(_targetProject.sourcesToBeMoced) ):
            cmakeMocInputVarName = "MOC_%s" % (_targetProject.name)
            cmakeMocInputVar = "${%s}" % (cmakeMocInputVarName)
            f.write("\nQT_WRAP_CPP( %s %s %s )\n" % (_targetProject.name, cmakeMocInputVarName, Join(_targetProject.sourcesToBeMoced)) )
            
        # write section that is specific for the project type        
        if( len(_targetProject.sources) ):
            f.write( "\n# Add target\n" )
            
            # add definitions
            if( len(_targetProject.privateDefinitions) ):
            	f.write( "ADD_DEFINITIONS(%s)\n" % Join(_targetProject.privateDefinitions) )
            
            # add sources
            if(_targetProject.type == "executable" ):
                f.write( "ADD_EXECUTABLE(%s %s %s)\n" % (_targetProject.name, cmakeMocInputVar, Join(_targetProject.sources)) )
                
            elif(_targetProject.type == "library" ):
                f.write( "ADD_LIBRARY(%s STATIC %s %s)\n" % (_targetProject.name, cmakeMocInputVar, Join(_targetProject.sources)) )
            
            elif(_targetProject.type == "dll" ):
                f.write( "ADD_LIBRARY(%s SHARED %s %s)\n" % (_targetProject.name, cmakeMocInputVar, Join(_targetProject.sources)) )
                
            else:
                raise NameError, "Unknown project type %s" % _targetProject.type

        # Find projects that must be generated. A separate list is used to ease debugging.
        projectsToGenerate = set()
        dependendChildProjects = _targetProject.DependendChildProjects(_recursive = 1)        
        for project in dependendChildProjects:
            # determine if we must Generate the project. If a child project will generate it, then leave it to the child.
            # This will prevent multiple generation of the same project.
            generateProject = not project in _generatedList
            if( generateProject ):
                for childProject in _targetProject.childProjects:
                    if( childProject.DependsOn(project) ):
                        generateProject = 0
            if( generateProject ):
                projectsToGenerate.add(project)
        f.write( "\n" )
        
        # add non-dependend child projects that have not yet been generated to projectsToGenerate
        for project in _targetProject.childProjectsNonDependend:
            if( not project in _generatedList ):
                projectsToGenerate.add(project)

        # generate child projects, and add a line with ADD_SUBDIRECTORY
        for project in projectsToGenerate:
            f.write( "ADD_SUBDIRECTORY(\"${BINARY_DIR}/%s\" \"${BINARY_DIR}/%s\")\n" % (project.binarySubfolder, project.binarySubfolder) )
            self.Generate(project, _binaryFolder, _generatedList, _knownProjectNames)
           
        # add dependencies
        f.write( "\n" )
        for project in dependendChildProjects:
            if( len(project.sources) ):
                f.write( "ADD_DEPENDENCIES(%s %s)\n" % (_targetProject.name, project.name) )
        
        f.close()

    def __GenerateWin32Header(self, _targetProject, _binaryFolder):
        """
        Generates the ProjectNameWin32.h header file for exporting/importing dll functions.
        """
        templateFilename = root + "/GBuild/Win32Header.h"
        templateOutputFilename = "%s/%s/%sWin32Header.h" % (_binaryFolder, _targetProject.binarySubfolder, _targetProject.name)

        assert os.path.exists(templateFilename), "File not found %s\n" % (templateFile)
        f = open(templateFilename, 'r')
        template = f.read()
        template = template.replace('${PROJECTNAME_UPPERCASE}', _targetProject.name.upper())
        template = template.replace('${PROJECTNAME}', _targetProject.name)

        # template.replace('${PROJECTNAME}', _targetProject.name())
        f.close()
        
        f = open(templateOutputFilename, 'w')
        f.write(template)
        f.close()
        
class Project:
    """
    Contains the data for the makefile (or vcproj) for a project.
    _name -- Name of the project, e.g. \"SampleApp\"
    _type -- Type of the project, should be \"executable\", \"library\" or \"dll\"

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
    self.useBefore -- A list of projects. This project must be used before the projects in this list.
    self.configFileSubpath -- The config file for the project. See above.
    self.sources -- Sources to be compiled for this target.
    self.privateDefinitions -- Definitions to be used by the pre-processor (only) when building this target.
    self.publicDefinitions -- Definitions to be used by the pre-processor when building this target or dependend targets.
    self.sourcesToBeMoced -- Sources for which a moc file must be generated.
    self.dlls -- Dlls to be installed in the binary folder for this target.
    self.useFileSubpath -- The use file of the project. See above.
    self.cmakeListsSubpath -- The cmake file that builds the project as a target
    self.childProjects -- Set of project instances. These projects have been added to self using AddProject.
    self.childProjectsNonDependend = Subset of self.childProjects. Contains projects that self doesn't depend on.
    self.publicIncludeFolders -- List of include search folders required to build a target that uses this project.
    self.publicLibraryFolders -- List of library search folders required to build a target that uses this project.
    self.publicLibraries -- List of linker inputs required to build a target that uses this project.
    """
    
    def __init__(self, _name, _type):
        self.publicIncludeFolders = []
        self.publicLibraryFolders = []
        self.publicLibraries = []
        self.sources = []
        self.privateDefinitions = []
        self.publicDefinitions = []
        self.sourcesToBeMoced = []
        self.name = _name
        self.dlls = []
        self.type = _type
        self.sourceRootFolder = os.path.normpath(os.path.dirname(Caller(1)[0])).replace("\\", "/")
        self.useBefore = []
        if( self.type == "dll" ):
            self.binarySubfolder = "library/%s" % (_name)
        else:
            self.binarySubfolder = "%s/%s" % (self.type, _name)
        self.configFileSubpath = "%s/%sConfig.cmake" % (self.binarySubfolder, _name)
        self.useFileSubpath = "%s/Use%s.cmake" % (self.binarySubfolder, _name)
        self.cmakeListsSubpath = "%s/CMakeLists.txt" % (self.binarySubfolder)
        self.childProjects = set()
        self.childProjectsNonDependend = set()
        
    def AddProject(self, _childProject, _dependency = 1):
        """ 
        Adds otherProject as a child. Adds all children of otherProject as children of self. 
        _dependency - Flag that states that self target is dependent on the _childProject target.
        Raises StandardError in case of a cyclic dependency.
        """
        if( self is _childProject ):
            raise DependencyError, "Project %s cannot be added to itself" % (_childProject.name)
            
        if( not _childProject in self.childProjects ):
            if( _dependency and _childProject.DependsOn(self) ):
                raise DependencyError, "Circular dependency detected during %s.AddProject(%s)" % (self.name, _childProject.name)
            self.childProjects.add( _childProject )
            if( not _dependency ):
                self.childProjectsNonDependend.add( _childProject )

    def AddSources(self, _listOfSourceFiles, _moc = 0, _checkExists = 1):
        """
        Adds items to self.sources. For each source file that is not an absolute path, self.sourceRootFolder is prefixed.
        Entries of _listOfSourceFiles may contain wildcards, such as src/*/*.h.
        If _moc, then a moc file is generated for each header file in _listOfSourceFiles.
        If _checkExists, then added sources (possibly after wildcard expansion) must exist on the filesystem, or an exception is thrown.
        """
        for sourceFile in _listOfSourceFiles:
			sources = self.__Glob(sourceFile)
			if( _checkExists and not len(sources) ):
				raise IOError, "Path file not found %s" % (sourceFile)
			self.sources.extend( sources )
			if( _moc ):
				self.sourcesToBeMoced.extend(sources)

    def AddDlls(self, _listOfDlls, _checkExists = 1):
        """
        Adds items to self.dlls. For each source file that is not an absolute path, self.sourceRootFolder is prefixed.
        Entries of _listOfDlls may contain wildcards, such as lib/*/*.dll.
        If _checkExists, then added dlls (possibly after wildcard expansion) must exist on the filesystem, or an exception is thrown.
        """
        for dll in _listOfDlls:
			dlls = self.__Glob(dll)
			if( _checkExists and not len(dlls) ):
				raise IOError, "Path file not found %s" % (dll)
			self.dlls.extend( dlls )
				
    def AddPrivateDefinitions(self, _listOfDefinitions):
        """
        Adds items to self.definitions. 
        """
        self.privateDefinitions.extend(_listOfDefinitions)
                
    def AddPublicDefinitions(self, _listOfDefinitions):
        """
        Adds items to self.definitions. 
        """
        self.publicDefinitions.extend(_listOfDefinitions)
                
    def AddPublicIncludeFolders(self, _listOfIncludeFolders):
        """
        Adds items to self.publicIncludeFolders. 
        If an item has a relative path, then it will be prefixed with _sourceRootFolder.
        Added include paths must exist on the filesystem.
        """
        for includeFolder in _listOfIncludeFolders:
            self.publicIncludeFolders.append( self.__FindPath(includeFolder) )
        
    def AddPublicLibraryFolders(self, _listOfLibraryFolders):
        """
        Adds items to self.publicLibraryFolders. 
        If an item has a relative path, then it will be prefixed with _sourceRootFolder.
        Added library paths must exist on the filesystem.
        """
        for libraryFolder in _listOfLibraryFolders:
            self.publicLibraryFolders.append( self.__FindPath(libraryFolder) )
        
    def AddPublicLibraries(self, _type, _listOfLibraries):
        """
        Adds items to self.publicLibraries. 
        _type - Should be \"debug\", \"optimzed\" or \"\".
        """
        assert _type in ("debug", "optimized", ""), "%s not any of (\"debug\", \"optimized\", \"\"" % (_type)
        for library in _listOfLibraries:
        	self.publicLibraries.append("%s %s" % (_type, library))
            
    def __FindPath(self, _path):
        """ 
        Tries to locate _path as an absolute path or as a path relative to self.sourceRootFolder. 
        Returns an absolute path, containing only forward slashes.
        Throws IOError if path was not found.
        """
        # Log( "Finding %s in %s\n" % (_path, self.sourceRootFolder) )
        
        path = _path
        if( not os.path.isabs(path) ):
            path = os.path.abspath("%s/%s" % (self.sourceRootFolder, path))
        if( not os.path.exists(path) ):
            raise IOError, "Path file not found %s" % (_path)
            
        path = path.replace("\\", "/")
        assert not HasBackSlash(path), path
        return path
        
    def __Glob(self, _path):
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
        
        for childProject in self.DependendChildProjects():
            if childProject in _skipList:
                continue
            if childProject is _otherProject or childProject.DependsOn(_otherProject, _skipList ):
                return 1
        return 0
        
    def DependendChildProjects(self, _recursive = 0):
        """
        Return a set of childProjects that self depends upon.
        If recursive is true, then dependend child projects of dependend child projects are also retrieved.
        """
        result = self.childProjects - self.childProjectsNonDependend
        if( _recursive ):
            moreResults = set()
            for project in result:
                moreResults.update( project.DependendChildProjects(_recursive) )
            result.update(moreResults)
        return result
        
    def UseBefore(self, _otherProject):
        """ 
        Indicate that self must be used before _otherProjects in a cmake file. 
        Throws DependencyError if _otherProject wants to be used before self.
        """
        if( _otherProjects.WantsToBeUsedBefore(self) ):
            raise DependencyError, "Cyclic use-before relation between %s and %s" % (self.name, _otherProject.name)
        self.useBefore.add(_otherProject)
        
    def WantsToBeUsedBefore(self, _otherProject, _stopList = None):
        """ 
        Return true if self wants to be used before _otherProject.
        _stopList - Used for robustness. Breaks the recursion in case of a cyclic dependency. 
        In this case, an assertion is raised, because this situation should never occur logically.
        """
        if _stopList is None:
            _stopList = []
        
        assert not self in _stopList
        _stopList.append(self)

        if( self is _otherProject ):
            return 0
            
        if( _otherProject in self.useBefore ):
            return 1
            
        for childProject in self.DependendChildProjects():
            if childProject.WantsToBeUsedBefore(_otherProject, _stopList):
                return 1
                
        return 0
           
    def GetProjectsToUse(self):
        """
        Determine a list of child projects to must be used (meaning: include the config and use file) to generate this project.
        Note that self is also included in this list.
        The list is sorted in the correct order, using Project.WantsToBeUsedBefore.
        """
        result = []
        
        projectsToUse = [project for project in self.DependendChildProjects(_recursive = 1)]
        assert not self in projectsToUse
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
        fileConfig = "%s/%s" % (_binaryFolder, self.configFileSubpath)
        f = open(fileConfig, 'w')
        
        # write header and some cmake fields
        f.write( "# File generated automatically by GBuild.py.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "SET( %s_FOUND \"TRUE\" )\n" % (self.name) )
        f.write( "SET( %s_INCLUDE_DIRS %s )\n" % (self.name, Join(self.publicIncludeFolders)) )
        f.write( "SET( %s_LIBRARY_DIRS %s )\n" % (self.name, Join(self.publicLibraryFolders)) )
        f.write( "SET( %s_LIBRARIES %s )\n" % (self.name, Join(self.publicLibraries)) )

    def GenerateUseFile(self, _binaryFolder):
        """
        Generates the UseXXX.cmake file for this project.
        """
        fileUse = "%s/%s" % (_binaryFolder, self.useFileSubpath)
        f = open(fileUse, 'w')
        
        # write header and some cmake fields
        f.write( "# File generated automatically by GBuild.py.\n" )
        f.write( "# DO NOT EDIT (changes will be lost)\n\n" )
        f.write( "INCLUDE_DIRECTORIES(${%s_INCLUDE_DIRS})\n" % (self.name) )
        f.write( "LINK_DIRECTORIES(${%s_LIBRARY_DIRS})\n" % (self.name) )
        f.write( "LINK_LIBRARIES(${%s_LIBRARIES})\n" % (self.name) )
        if( len(self.publicDefinitions) ):
        	f.write( "ADD_DEFINITIONS(%s)\n" % (Join(self.publicDefinitions)) )
     