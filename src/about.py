## @package about
# Definition of the About class.
import ConfigParser

class About:
    ''' Class to store about information. '''
    def __init__(self):
        # file config
        self.section = "About"
        self.section_name = "name"
        self.section_version = "version"
        self.section_description = "description"
        self.section_author = "author"
        # information
        self.name = "Default name"
        self.version = "0.0"
        self.description = "Default description."
        self.author = "Default author"
        
    def __eq__(self, other):
        if isinstance(other, About):
            res = self.name == other.getName()
            res &= self.version == other.getVersion()
            res &= self.description == other.getDescription()
            res &= self.author == other.getAuthor()
            return res   
        else:
            return NotImplemented
    
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def getName(self):
        return self.name

    def getVersion(self):
        return self.version

    def getDescription(self):
        return self.description

    def getAuthor(self):
        return self.author
    
    def read(self, filename):
        ''' Read the about information from file. '''
        parser = ConfigParser.ConfigParser()
        parser.read(filename)
        if not parser.has_section(self.section):
            raise Exception("About section not found")
        if parser.has_option(self.section, self.section_name):
            self.name = parser.get(self.section, self.section_name)
        if parser.has_option(self.section, self.section_version):
            self.version = parser.get(self.section, self.section_version)
        if parser.has_option(self.section, self.section_description):
            self.description = parser.get(self.section, self.section_description)
        if parser.has_option(self.section, self.section_author):
            self.author = parser.get(self.section, self.section_author)

    def write(self, filename):
        ''' Write the about information to file. '''
        parser = ConfigParser.ConfigParser()
        parser.add_section(self.section)
        parser.set(self.section, self.section_name, self.name)
        parser.set(self.section, self.section_version, self.version)
        parser.set(self.section, self.section_description, self.description)
        parser.set(self.section, self.section_author, self.author)
        # write
        aboutFile = open( filename, 'w' )
        parser.write(aboutFile)
        aboutFile.close()
        