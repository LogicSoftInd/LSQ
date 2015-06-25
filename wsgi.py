import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = sys.stderr
from app import app as application