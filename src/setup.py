## @package setup
# Python script used to generate executables.
# Depends on py2exe: http://www.py2exe.org
from distutils.core import setup
import os
# Added options for setup
import py2exe #@UnusedImport
from about import About

class exeSetup():
    ''' Helper class to generate windows executable.'''
    def __init__(self):
        pathToResources = "../resources/"
        pathToSrc = "../src/"
        # Resources of the setup script
        self.resources = []
        # Files at root level
        self.__addToResources("../readme.txt", ".")
        self.__addToResources("../license.txt", ".")
        # Resource files to add to bin folder.
        self.__addToResources(pathToResources, "resources")
        # Doc files to add to bin folder.
        self.__addToResources("../doc/html/", "doc/html")
        self.__addToResources("../doc/html/search/", "doc/html/search")
        # script
        self.script = pathToSrc + "csnGUI.py"
        self.icon_resource = pathToResources + "Laticauda_colubrina.ico"
        # options
        about = About()
        about.read( pathToResources + "about.txt")
        self.name = about.getName()
        self.version = about.getVersion()
        self.description = about.getDescription()
        self.author = about.getAuthor()
    
    def run(self):
        ''' Run the setup. '''
        setup(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            console=[ 
                {
                    "script": self.script,
                    "icon_resources": [(1, self.icon_resource)]
                }
            ],
            data_files = self.resources )
        
    def __addToResources(self, origin, destinationDir):
        ''' Add files/folder to the self.resources var.'''
        if os.path.isfile(origin):
            pair = destinationDir, [origin]
            self.resources.append(pair)
        else:
            for f1 in os.listdir(origin):
                f2 = origin + f1
                if os.path.isfile(f2): # skip directories
                    pair = destinationDir, [f2]
                    self.resources.append(pair)

if __name__ == "__main__":
    mainSetup = exeSetup()
    mainSetup.run()
