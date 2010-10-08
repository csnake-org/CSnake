import ConfigParser
from csnListener import ChangeEvent
import logging
import shutil

latestFileFormatVersion = 1.0

class Options:
    def __init__(self):
        # options
        self.__contextFilename = ""
        self.__askToLaunchIDE = False
        # listeners
        self.__listeners = []
        # logger
        self.__logger = logging.getLogger("CSnake")
 
    def GetContextFilename(self):
        """ Get the context file name. """
        return self.__contextFilename

    def SetContextFilename(self, value):
        """ Set the context file name. """
        self.__contextFilename = value

    def GetAskToLaunchIDE(self):
        return self.__askToLaunchIDE

    def Load(self, filename):
        """ Load an option file. """
        # parser
        parser = ConfigParser.ConfigParser()
        parser.read([filename])
        # check main section
        mainSection = "CSnake"
        if not parser.has_section(mainSection):
            raise IOError("Cannot read options, no 'CSnake' section.")
        # check version number
        version = 0.0
        if parser.has_option(mainSection, "version"):
            version = float(parser.get(mainSection, "version"))
        # read with proper reader
        if version == 0.0:
            self.__Read00( parser )
        elif version == 1.0:
            self.__Read10( parser )
        else:
            raise IOError("Cannot read options, unknown 'version':%s." % version)
        # backup and save in new format for old ones
        if version < latestFileFormatVersion:
            newFileName = "%s.bk" % filename
            shutil.copy(filename, newFileName)
            self.Save(filename)
        
    def __Read10(self, parser):
        """ Read options file version 1.0. """ 
        mainSection = "CSnake"
        # last open context
        self.__contextFilename = parser.get(mainSection, "contextFilename")
        # ask to launch ide
        self.__askToLaunchIDE = parser.get(mainSection, "askToLaunchIDE") == str(True)

    def __Read00(self, parser):
        """ Read options file version 0.0. """ 
        mainSection = "CSnake"
        # last open context
        self.__contextFilename = parser.get(mainSection, "currentguisettingsfilename")
        # ask to launch ide
        self.__askToLaunchIDE = parser.get(mainSection, "asktolaunchvisualstudio") == str(True)
    
    def Save(self, filename):
        parser = ConfigParser.ConfigParser()
        section = "CSnake"
        parser.add_section(section)
        parser.set(section, "contextFilename", self.__contextFilename)
        parser.set(section, "askToLaunchIDE", self.__askToLaunchIDE)
        parser.set(section, "version", latestFileFormatVersion)
        f = open(filename, 'w')
        parser.write(f)
        f.close()

    def HasField(self, field):
        """ Returns true if class has this attribute. Used in xrcbinder::BoundControl. """
        return hasattr(self, field)

    def GetField(self, field):
        """ Get the value of the attribute. Used in xrcbinder::BoundControl. """
        return getattr(self, field)
    
    def SetField(self, field, value):
        """ Set the value of the attribute. Used in xrcbinder::BoundControl. """
        # Check it the field exists
        if not hasattr(self, field):
            self.__logger.warn("SetField with wrong field.")
            return False
        # Set the field value if different from the current one
        if getattr(self, field) != value:
            # set the attribute
            setattr(self, field, value)
            # notify the listeners
            self.__NotifyListeners(ChangeEvent(self))
    
    def __NotifyListeners(self, event):
        for listener in self.__listeners:
            listener.Update(event)
        
    def AddListener(self, listener):
        if not listener in self.__listeners:
            self.__listeners.append(listener)
