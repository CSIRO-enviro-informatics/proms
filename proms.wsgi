import sys
import logging
sys.path.insert(0, '/var/www/proms/')
logging.basicConfig(stream=sys.stderr)

from app import app as application
