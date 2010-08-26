import ConfigParser

class Options:
    def __init__(self):
        self.__contextFilename = ""
        self.__askToLaunchIDE = False

    def GetContextFilename(self):
        return self.__contextFilename

    def SetContextFilename(self, value):
        self.__contextFilename = value

    def GetAskToLaunchIDE(self):
        return self.__askToLaunchIDE
    
    def Load(self, filename):
        parser = ConfigParser.ConfigParser()
        parser.read([filename])
        section = "CSnake"
        self.__contextFilename = parser.get(section, "contextFilename")
        if parser.has_option(section, "askToLaunchIDE"):
            self.__askToLaunchIDE = parser.get(section, "askToLaunchIDE") == str(True)
        
    def Save(self, filename):
        parser = ConfigParser.ConfigParser()
        section = "CSnake"
        parser.add_section(section)
        parser.set(section, "contextFilename", self.__contextFilename)
        parser.set(section, "askToLaunchIDE", self.__askToLaunchIDE)
        parser.set(section, "version", "1.0")
        f = open(filename, 'w')
        parser.write(f)
        f.close()
