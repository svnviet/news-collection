import time
from abc import abstractmethod
from functools import wraps

import requests
from pymongo import MongoClient


class SyncBase:
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

    def retry_on_proxy(self, max_attempts=5, delay=2):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                last_exception = None
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(self, *args, **kwargs)
                    except Exception as e:
                        print(f"[Attempt {attempt}] Error: {e}")
                        last_exception = e
                        time.sleep(delay)
                raise RuntimeError(f"All {max_attempts} attempts failed.") from last_exception
            return wrapper
        return decorator

    def load_proxies(self):
        try:
            res = requests.get(self.proxy_url, timeout=10)
            if res.ok:
                lines = res.text.strip().splitlines()
                return [f"http://{p.strip()}" for p in lines if p.strip()]
        except Exception as e:
            print(f"Failed to fetch proxies: {e}")
        return []


