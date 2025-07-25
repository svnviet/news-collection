import logging
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_DIR = os.path.abspath(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
    )
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    SOURCE_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
    SECRET_KEY = os.environ.get("SECRET_KEY", default="your_secret_key")
    # SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "app.db")
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    DB_PASSWORD = os.environ.get("DB_PASSWORD", default="<PASSWORD>")
    DB_USER = os.environ.get("DB_USER", default="<DB_USER>")
    DB_NAME = os.environ.get("DB_NAME", default="<DB_USER>")
    DB_HOST = os.environ.get("DB_HOST", default="<DB_HOST>")
    W3_URL = os.environ.get("W3_URL", default="")
    MONGO_URI = f"mongodb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:27017/{DB_NAME}?authSource=admin"
    # MONGO_URI = "mongodb://localhost:27017/vn-news"
    BASE_URL = os.environ.get("BASE_URL", default="http:localhost:5000")
    CRAWL_URL = os.environ.get("CRAWL_URL", default="")
    # Logger config
    LOG_LEVEL = logging.DEBUG
    LOG_DIR = os.path.join(SOURCE_DIR, "logs")
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_FILE = os.path.join(LOG_DIR, "app.log")
    LOG_FORMAT = "('%(asctime)s - %(levelname)s - %(message)s')"
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
