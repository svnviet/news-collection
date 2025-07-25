import logging

from flask_pymongo import PyMongo
from pymongo import MongoClient
from . import Config

config = Config()
db = PyMongo()
logging.getLogger("pymongo").setLevel(logging.WARNING)
client = MongoClient(config.MONGO_URI)

client.get_database()["vn-news"].create_index(
    {"source_type": 1, "published_date": -1}
)
