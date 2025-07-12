import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

vn_url = "https://vnexpress.net/"
base_url = "http://127.0.0.1:5000/"
detail_url = "http://127.0.0.1:5000/vn-vi/news/"
DB_PASSWORD = os.environ.get("DB_PASSWORD", default="<PASSWORD>")
DB_USER = os.environ.get("DB_USER", default="<DB_USER>")
DB_NAME = os.environ.get("DB_NAME", default="<DB_USER>")
DB_HOST = os.environ.get("DB_HOST", default="<DB_HOST>")
MONGO_URI = f"mongodb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:27017/{DB_NAME}?authSource=admin"
client = MongoClient(MONGO_URI)