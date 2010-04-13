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
        # Resource files to add to bin folder.
        self.resources = []
        for resFile in os.listdir(pathToResources):
            f1 = pathToResources + resFile
            if os.path.isfile(f1): # skip directories
                f2 = "resources", [f1]
                self.resources.append(f2)
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
            windows=[ 
                {
                    "script": self.script,
                    "icon_resources": [(1, self.icon_resource)]
                }
            ],
            data_files = self.resources )

if __name__ == "__main__":
    mainSetup = exeSetup()
    mainSetup.run()
