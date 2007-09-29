import csnBuild
import csnUtility
import os.path

def LoadThirdPartyModule(_subFolder, _name):
	""" Loads third party module _name from subfolder _subFolder of the third party folder """
	folder = "D:\\Users\\Maarten\\Code\\ThirdParty\\thirdParty\\%s" % (_subFolder)
	return csnUtility.LoadModule(folder, _name)
	
def AddCilabLibraryModules(_project, _libmodules):
	""" Creates a new library from a set of libmodules. Used to build libraries in CilabModules """
	# add sources    
	for libModule in _libmodules:
		_project.AddPublicIncludeFolders(["libmodules/%s/include" % libModule])
		_project.AddPublicIncludeFolders(["libmodules/%s/src" % libModule])
		_project.AddSources(["libmodules/%s/include/*.h" % libModule], _checkExists = 0)
		_project.AddSources(["libmodules/%s/src/*.c??" % libModule], _checkExists = 0)

def AddApplications(_holderProject, _applicationDependenciesList, _modules, _modulesFolder = "Applications"):
    """ 
    Creates application projects from _modulesFolder and adds them to _holderProject.
    Each source file in each subfolder of _modulesFolder corresponds to one application.
    _modules - Subfolders of _modulesFolder that are used to find the application sources.
    _applicationDependenciesList - List of projects that each application is dependent on.
    """
    for module in _modules:
        moduleFolder = "%s/%s" % (_modulesFolder, module)
        sourceFiles = _holderProject.Glob("%s/*.cpp" % moduleFolder)
        
        prefix = os.path.basename(_modulesFolder)
        for sourceFile in sourceFiles:
            (name, ext) = os.path.splitext( os.path.basename(sourceFile) )
            app = csnBuild.Project("evo%s.%s" % (prefix, name), "executable", 2)
            app.AddPublicIncludeFolders([moduleFolder]) 
            app.AddProjects(_applicationDependenciesList)
            app.AddSources([sourceFile])
            _holderProject.AddProjects([app])
