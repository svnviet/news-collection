import random
from abc import abstractmethod

import requests
from pymongo import MongoClient


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SyncBase(metaclass=SingletonMeta):
    """
    This base class for crawling data from rss - interaction with database and other services rss
    """

    MONGO_URI = "mongodb://localhost:27017/vn-news"
    mongo_uri = MONGO_URI
    client = MongoClient(mongo_uri)
    db = client["vn-news"]  # Create or connect to a database
    news_collection = db["vn-news"]
    news_errors = ["ads", "removed", "podcast", "video"]
    source_types = ["VNExpress", "NLD"]
    proxy_url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=vn&proxy_format=protocolipport&format=text&timeout=20000"

    def __init__(self, rss_url, local_url):
        self.rss_url = rss_url
        self.local_url = local_url

    @abstractmethod
    def get_rss_list(self):
        pass

    @abstractmethod
    def insert_rss(self):
        pass

    def request(self, url, method="get", headers=None, proxies=None, **kwargs):
        if not proxies:
            raise ValueError("No proxies available.")
        proxy = random.choice(proxies)
        print(f"→ Using proxy: {proxy}")
        proxies = {"http": proxy, "https": proxy}
        return requests.request(method, url, headers=headers, proxies=proxies, timeout=5, **kwargs)
