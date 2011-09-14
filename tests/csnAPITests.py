import csnAPIPublic #@UnusedImport (in theory...)
import unittest

class csnAPITests(unittest.TestCase):
    
    def setUp(self):
        """ Run before test. """

    def tearDown(self):
        """ Run after test. """

    def testImport(self):
        """ Test that non imported class stay private. """
        self.assertRaises(NameError, lambda : Version("1.2.3") ) #@UndefinedVariable
        self.assertRaises(NameError, lambda : csnProject.Project("name", "type") ) #@UndefinedVariable
