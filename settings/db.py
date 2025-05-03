import logging

from flask_pymongo import PyMongo

db = PyMongo()
logging.getLogger("pymongo").setLevel(logging.WARNING)
