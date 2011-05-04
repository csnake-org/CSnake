## @package csnListener
# Definition of observer pattern related classes. 

class Event:
    """ Generic event class. """
    def __init__(self, code, source):
        self.__code = code
        self.__source = source

    def GetCode(self):
        return self.__code
    
    def GetSource(self):
        return self.__source
    
    def ToString(self):
        if self.IsNull():
            return "null"
        elif self.IsChange():
            return "change"
        elif self.IsProgress():
            return "progress"
        else:
            return None
        
    def GetNullCode(self):
        return 0
    
    def GetChangeCode(self):
        return 1

    def GetProgressCode(self):
        return 2
    
    def IsNull(self):
        return self.__code == self.GetNullCode()
    
    def IsChange(self):
        return self.__code == self.GetChangeCode()

    def IsProgress(self):
        return self.__code == self.GetProgressCode()
    
class ChangeEvent(Event):
    """ Change event class. """
    def __init__(self, source):
        Event.__init__(self, self.GetChangeCode(), source)

class ProgressEvent(Event):
    """ Change event class. """
    def __init__(self, source, progress, message = ""):
        self.__progress = progress
        self.__message = message
        Event.__init__(self, self.GetProgressCode(), source)
        
    def GetProgress(self):
        return self.__progress

    def GetMessage(self):
        return self.__message
         
class Listener:
    """ Generic listener class. """
    def __init__(self, source):
        self._source = source
        
    def GetSource(self):
        """ Get the listener source. """
        return self._source
    
    def Update(self):
        """ Abstract. """

class ChangeListener(Listener):
    """ Listener for ChangeEvent. The listener source needs to implement StateChanged(event). """   
    def Update(self, event):
        """ Call the source to tell it the state has changed. """
        if event.IsChange():
            self._source.StateChanged(event)

class ProgressListener(Listener):
    """ Listener for ProgressEvent. The listener source needs to implement ProgressChanged(event). """   
    def Update(self, event):
        """ Call the source to tell it the state has changed. """
        if event.IsProgress():
            self._source.ProgressChanged(event)
        