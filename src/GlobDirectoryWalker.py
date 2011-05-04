## @package GlobDirectoryWalker
# Definition of the directory Walker class. 
import os
import fnmatch

class Walker:
    # a forward iterator that traverses a directory tree

    def __init__(self, directory, patterns, excludedFoldersList = None):
        self.stack = [directory]
        self.patterns = patterns
        self.files = []
        self.index = 0
        if excludedFoldersList is None:
            self.excludedFoldersList = []
        else:
            self.excludedFoldersList = excludedFoldersList

    def __getitem__(self, index):
        while 1:
            try:
                okay = False
                while not okay:
                    file = self.files[self.index]
                    self.index = self.index + 1
                    # skip if file is a folder in excludedFoldersList
                    fullname = os.path.join(self.directory, file)
                    okay = not( os.path.isdir(fullname) and file in self.excludedFoldersList )
            except IndexError:
                # pop next directory from stack
                self.directory = self.stack.pop()
                self.files = os.listdir(self.directory)
                self.index = 0
            else:
                # got a filename
                fullname = os.path.join(self.directory, file)
                if os.path.isdir(fullname) and not os.path.islink(fullname):
                    self.stack.append(fullname)
                for pattern in self.patterns:
                    if fnmatch.fnmatch(file, pattern):
                        return fullname
