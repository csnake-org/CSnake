import ConfigParser

class Options:
    def __init__(self):
        self.contextFilename = ""
        self.askToLaunchIDE = False

    def Load(self, filename):
        parser = ConfigParser.ConfigParser()
        parser.read([filename])
        section = "CSnake"
        self.contextFilename = parser.get(section, "contextFilename")
        if parser.has_option(section, "askToLaunchIDE"):
            self.askToLaunchIDE = parser.get(section, "askToLaunchIDE") == str(True)
        
    def Save(self, filename):
        parser = ConfigParser.ConfigParser()
        section = "CSnake"
        parser.add_section(section)
        parser.set(section, "contextFilename", self.contextFilename)
        parser.set(section, "askToLaunchIDE", self.askToLaunchIDE)
        parser.set(section, "version", "1.0")
        f = open(filename, 'w')
        parser.write(f)
        f.close()
