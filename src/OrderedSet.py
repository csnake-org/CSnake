## @package OrderedSet
# Definition of the OrderedSet class. 

class OrderedSet(list):
    """ Class that stores an ordered set list. """
    def __init__(self):
        pass

    def __sub__(self, _other):
        """
        Returns self - other (elements of self which are not in _other)
        """
        result = OrderedSet()
        for x in self:
            if not x in _other:
                result.add(x)
        return result 
        
    def add(self, element):
        """Add an element to the right side of the OrderedSet."""
        if not element in self:
            list.append(self, element)

    def append(self, element):
        """Add an element to the right side of the OrderedSet."""
        self.add(element)

    def update(self, iterable):
        """Extend the right side of the OrderedSet with elements from the iterable."""
        for element in iterable:
            self.add(element)
