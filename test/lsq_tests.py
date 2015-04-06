import unittest

# Import the application
from app import app as lsq

class LSQTestCase(unittest.TestCase):

    def setUp(self):
        self.app = lsq.app.test_client()

    def tearDown(self):
        pass
        
    def test_homepage_200(self):
        rv = self.app.get('/')
        assert 200 == rv.status_code

if __name__ == '__main__':
    unittest.main()
