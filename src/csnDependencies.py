import csnProject
import OrderedSet
import logging

class DependencyError(StandardError):
    """ Used when there is a cyclic dependency between CSnake projects. """
    pass
    
class Manager:
    def __init__(self, _project):
        self.project = _project
        self.projects = OrderedSet.OrderedSet()
        self.projectsNonRequired = OrderedSet.OrderedSet()
        self.projectsIncludedInSolution = OrderedSet.OrderedSet()
        self.useBefore = []
        self.isTopLevel = False
        # logger
        self.__logger = logging.getLogger("CSnake")
        
    def AddProjects(self, _projects, _dependency = True, _includeInSolution = True):
        for project in _projects:
            projectToAdd = csnProject.ToProject(project)
            if projectToAdd.MatchesFilter() or projectToAdd in self.GetProjects():
                continue
                    
            if self.project is projectToAdd:
                raise DependencyError, "Project %s cannot be added to itself" % (projectToAdd.name)
                
            if not projectToAdd in self.projects:
                if _dependency and projectToAdd.dependenciesManager.DependsOn(self.project):
                    raise DependencyError, "Circular dependency detected during %s.AddProjects(%s)" % (self.project.name, projectToAdd.name)
                self.projects.add( projectToAdd )
                if not _dependency:
                    self.projectsNonRequired.add( projectToAdd )
                if _includeInSolution:
                    self.projectsIncludedInSolution.add( projectToAdd )
                    
    def DependsOn(self, _otherProject, _skipList = None):
        """ 
        Returns true if self is (directly or indirectly) dependent upon _otherProject. 
        _otherProject - May be a project, or a function returning a project.
        _skipList - Used to not process project twice during the recursion (also prevents infinite loops).
        """
        if _skipList is None:
            _skipList = []
        
        otherProject = csnProject.ToProject(_otherProject)
        assert not self.project in _skipList, "\n\nError: %s should not be in stoplist" % (self.project.name)
        _skipList.append(self.project)
        for requiredProject in self.GetProjects(_onlyRequiredProjects = 1):
            if requiredProject in _skipList:
                continue
            if requiredProject is otherProject or requiredProject.dependenciesManager.DependsOn(otherProject, _skipList ):
                return 1
        return 0
        
    def GetProjects(self, _recursive = False, _onlyRequiredProjects = False, _includeSelf = False, _onlyPublicDependencies = False, _onlyNonRequiredProjects = False, _skipList = [], _stack = []):
        """
        Returns list of all projects associated with this project.
        _recursive -- If true, returns not only child projects but all projects in the tree below this project.
        _onlyRequiredProjects -- If true, only projects that this project requires are returned.
        """
        if self.project in _stack:
            if _onlyRequiredProjects:
                namelist = []
                foundStart = False
                for project in _stack:
                    if project == self.project:
                        foundStart = True
                    if foundStart:
                        namelist.append(project.name)
                namelist.append(self.project.name)
                self.__logger.Warn("Cyclic dependency: %s" % namelist)
            return OrderedSet.OrderedSet()
        _stack = _stack + [self.project]
            
        directDependencies = OrderedSet.OrderedSet()
        toSubtract = OrderedSet.OrderedSet()
        toAdd = OrderedSet.OrderedSet()
        if _onlyNonRequiredProjects:
            toAdd.update(self.projectsNonRequired)
        else:
            toAdd.update(self.projects)

        if _onlyRequiredProjects:
            toSubtract.update(self.projectsNonRequired)
        directDependencies.update(toAdd - toSubtract)

        if _recursive:
            fullDependencies = OrderedSet.OrderedSet()
            for project in directDependencies:
                fullDependencies.update(
                    project.dependenciesManager.GetProjects(
                        _recursive,
                        _onlyRequiredProjects,
                        True,
                        _onlyPublicDependencies,
                        _onlyNonRequiredProjects,
                        _skipList,
                        _stack
                    )
                )
            dependencies = fullDependencies
        else:
            dependencies = directDependencies
            
        if _includeSelf:
            dependencies.add(self.project)
        return dependencies
        
    def UseBefore(self, _otherProject):
        """ 
        Sets a flag that says that self must be used before _otherProjects in a cmake file. 
        Throws DependencyError if _otherProject wants to be used before self.
        _otherProject - May be a project, or a function returning a project.
        """
        otherProject = csnProject.ToProject(_otherProject)
        if otherProject.dependenciesManager.WantsToBeUsedBefore(self.project):
            raise DependencyError, "Cyclic use-before relation between %s and %s" % (self.project.name, otherProject.name)
        self.useBefore.append(otherProject)
        
    def WantsToBeUsedBefore(self, _otherProject):
        """ 
        Return true if self wants to be used before _otherProject.
        _otherProject - May be a project, or a function returning a project.
        """
        otherProject = csnProject.ToProject(_otherProject)
        
        #if otherProject in self.GetProjects(_recursive = 1, _onlyRequiredProjects = 1):
        #    return 1
        #if self.project in otherProject.dependenciesManager.GetProjects(_recursive = 1, _onlyRequiredProjects = 1):
        #    return 0
        
        if self.project is otherProject:
            return 0
            
        if otherProject in self.useBefore:
            return 1
            
        for requiredProject in self.GetProjects(_recursive = 1, _onlyRequiredProjects = 1):
            if otherProject in requiredProject.dependenciesManager.useBefore:
                return 1
                
        return 0
           
    def ProjectsToUse(self):
        """
        Determine a list of projects that must be used (meaning: include the config and use file) to generate this project.
        Note that self is always the last project in this list.
        The list is sorted in the correct order, using Project.WantsToBeUsedBefore.
        """
        result = []
        
        projectsToUse = [project for project in self.GetProjects(_recursive = 1, _onlyRequiredProjects = 1)]
        assert not self in projectsToUse, "\n\nError: %s should not be in projectsToUse" % (self.project.name)
        projectsToUse.append(self.project)
        
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
                if otherProject.dependenciesManager.WantsToBeUsedBefore(project):
                    assert not otherProject is self.project, "\n\nLogical error: %s cannot be used before %s" % (self.project.name, project.name)
                    skipThisProjectForNow = 1
            if skipThisProjectForNow:
                projectsToUse.insert(0, project)
                continue
            else:
                result.append(project)
          
        # ensure that self.project is the first entry in the result
        result.remove(self.project)
        result.insert(0,self.project)
        return result

    def WriteDependencyStructureToXML(self, filename):
        """
        Writes an xml file containing the dependency structure for this project and its dependency projects.
        """
        f = open(filename, 'w')
        self.WriteDependencyStructureToXMLImp(f)
        f.close()

    def WriteDependencyStructureToXMLImp(self, f, indent = 0):
        """
        Helper function.
        """
        for _ in range(indent):
            f.write(' ')
        f.write("<%s>" % self.project.name)
        for project in self.project.GetProjects(_onlyRequiredProjects = 1):
            project.dependenciesManager.WriteDependencyStructureToXMLImp(f, indent + 4)
        f.write("</%s>\n" % self.project.name)
