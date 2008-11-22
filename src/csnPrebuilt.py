import os
import csnUtility

class ProjectRelocator:
    """ 
    This class relocates projects to use the prebuilt projects folder.
    It scans a target project for all child projects. For each child project, it checks if the project is available in the
    prebuilt projects folder. If so, it labels the project as "prebuilt", and sets the use file and config file to the ones
    from the prebuilt project.
    
    If you want to relocate a project p, add a subfolder (with name p.name) in the relocated projects folder.
    This subfolder should have a csnake file called csnRelocate + p.name + .py. 
    The filename may have only one period (for the extension); replace any other period with underscore. E.g. for vtk, 
    you would have PrebuiltProjectFolder/VTK-5.1/csnRelocateVTK-5_1.py .
    """
    
    def Do(self, _targetProject, _prebuiltProjectsFolder):
        if _prebuiltProjectsFolder == "":
            return
        for project in _targetProject.GetProjects(_recursive = 1):
            prebuiltProjectFolder = "%s/%s" % (_prebuiltProjectsFolder, project.name)
            if os.path.exists(prebuiltProjectFolder):
                self.__Relocate(project, prebuiltProjectFolder)
            elif False:
                print "Not relocating project %s (no folder %s)\n" % (project.name, prebuiltProjectFolder)
                
    def __Relocate(self, _project, _prebuiltProjectFolder):
        print "Relocating project %s\n" % _project.name
        name = _project.name.replace(".", "_")
        module = csnUtility.LoadModule(_prebuiltProjectFolder, "csnRelocate" + name)
        self.prebuiltProjectFolder = _prebuiltProjectFolder
        self.project = _project
        module.Relocate(_project, self)

    def InitializeRelocatedProject(self):
        self.project.sources = []
        self.project.type = "prebuilt"
        self.project.ResolvePathsOfFilesToInstall(self.prebuiltProjectFolder)
        
    def DefaultConfigureConfigAndUseFile(self):        
        self.project.configFilePath = "%s/%sConfig.cmake" % (self.prebuiltProjectFolder, self.project.name)
        self.project.useFilePath = "%s/Use%s.cmake" % (self.prebuiltProjectFolder, self.project.name)
        self.ConfigureFile( "%s.in" % self.project.configFilePath, self.project.configFilePath )
        
    def ConfigureFile(self, _fromFile, _toFile, _folder = ""):
        if not os.path.isabs(_fromFile):
            _fromFile = "%s/%s" % (_folder, _fromFile)
        if not os.path.isabs(_toFile):
            _toFile = "%s/%s" % (_folder, _toFile)
            
        f = open(_fromFile, 'r')
        text = f.read()
        f.close()
        
        text = text.replace("${PrebuiltProjectFolder}", self.prebuiltProjectFolder)
        text = text.replace("${ProjectSourceRootFolder}", self.project.sourceRootFolder)
        f = open(_toFile, 'w')
        f.write(text)
        f.close()
