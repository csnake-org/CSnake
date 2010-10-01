
class Event:
    """ Generic event class. """
    def __init__(self, code, source):
        self._code = code
        self._source = source

    def GetCode(self):
        return self._code
    
    def GetSource(self):
        return self._source
    
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
        return self._code == self.GetNullCode()
    
    def IsChange(self):
        return self._code == self.GetChangeCode()

    def IsProgress(self):
        return self._code == self.GetProgressCode()
    
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
        
    def Update(self):
        """ Abstract. """

class ChangeListener(Listener):
    """ Listener for ChangeEvent. """   
    def Update(self, event):
        """ Call the source to tell it the state has changed. """
        if event.IsChange():
            self._source.StateChanged(event)

class ProgressListener(Listener):
    """ Listener for ProgressEvent. """   
    def Update(self, event):
        """ Call the source to tell it the state has changed. """
        if event.IsProgress():
            self._source.ProgressChanged(event)
        