import logging
import jwt

from flask_pymongo import PyMongo
from flask_migrate import Migrate
from config import Config

config = Config()
db = PyMongo()
migrate = Migrate()
jwt = jwt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable Flask-PyMongo debug logs
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("flask_pymongo").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)  # Optional: Disable Flask request logs
