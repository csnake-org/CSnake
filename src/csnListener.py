
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
        else:
            return None
        
    def GetNullCode(self):
        return 0
    
    def GetChangeCode(self):
        return 1
    
    def IsNull(self):
        return self._code == self.GetNullCode()
    
    def IsChange(self):
        return self._code == self.GetChangeCode()
    
class ChangeEvent(Event):
    """ Change event class. """
    def __init__(self, source):
        Event.__init__(self, self.GetChangeCode(), source)
        
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
        