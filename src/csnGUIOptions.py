import ConfigParser
from csnListener import ChangeEvent
import logging

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
