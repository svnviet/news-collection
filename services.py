import random

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

from sync.vnexpress import collection, insert_or_get_detail
from sync.nld import SyncNLD

sync_nld = SyncNLD()

vn_url = "https://vnexpress.net/"
base_url = "http://127.0.0.1:5000/"
detail_url = "http://127.0.0.1:5000/vn-vi/VNExpress/"


class NewsService:
    MONGO_URI = "mongodb://localhost:27017/vn-news"
    mongo_uri = MONGO_URI
    client = MongoClient(mongo_uri)
    db = client["vn-news"]  # Create or connect to a database
    news_collection = db["vn-news"]

    def __init__(self):
        pass

    def get_news(self):
        news = self._get_news_home()
        data = []
        hot_news = []
        max_slide_count = 10
        slide_count = 0
        for idx, item in enumerate(news):
            description = item.get("description")
            desc_soup = BeautifulSoup(description, "html.parser")
            img_tag = desc_soup.find("img")
            image_url = img_tag["src"] if img_tag else None
            item.update({"image_url": image_url})
            item["_id"] = str(item["_id"])
            if slide_count < max_slide_count:
                if image_url:
                    slide_count += 1
                    hot_news.append(item)
            else:
                data.append(item)
        return data, hot_news

    def load_more_news(self, page, per_page):
        merged_articles = []
        source_types = sync_nld.source_types
        per_page_s = per_page // len(source_types)

        for source in source_types:
            articles = self._get_news_by_source(source, page, per_page_s)
            merged_articles.extend(articles)

        random.shuffle(merged_articles)
        for article in merged_articles:
            article["_id"] = str(article["_id"])

        return merged_articles

    def _get_news_by_source(self, source_type, page, limit):
        skip = (page - 1) * limit
        match_stage = {
            "$match": {
                "source_type": source_type,
            }
        }

        pipeline = [
            match_stage,
            {"$sort": {"published": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]

        return list(self.news_collection.aggregate(pipeline))

    @staticmethod
    def get_detail(slug, source):
        if "https://" in slug:
            return slug, None
        link = ""
        detail_data = None
        if source == "VNExpress":
            link = "https://vnexpress.net/" + slug
            detail_data = insert_or_get_detail(link)
        elif source == "NLD":
            link = "https://nld.com.vn/" + slug
            detail_data = sync_nld.insert_or_get_detail(link)
        return link, detail_data

    def get_news_related(self, page, per_page):
        merged_articles = []
        source_types = sync_nld.source_types
        per_page_s = per_page // len(source_types)

        for source in source_types:
            articles = self._get_news_by_source(source, page, per_page_s)
            merged_articles.extend(articles)

        random.shuffle(merged_articles)

        data = []
        hot_news = []
        max_slide_count = 5
        slide_count = 0
        main_item = None
        for idx, item in enumerate(merged_articles):
            if main_item is None:
                try:
                    _, detail_news = self.get_detail(item['link'], item['source_type'])
                    if detail_news:
                        main_item = detail_news
                        continue
                except Exception:
                    pass
            description = item.get("description")
            desc_soup = BeautifulSoup(description, "html.parser")
            img_tag = desc_soup.find("img")
            image_url = img_tag["src"] if img_tag else None
            item.update({"image_url": image_url})
            item["_id"] = str(item["_id"])
            if slide_count < max_slide_count:
                if image_url:
                    slide_count += 1
                    hot_news.append(item)
            else:
                data.append(item)

        return data, hot_news, main_item

    def _get_news_related(self, limit=10):
        pipeline = [
            {
                "$group": {
                    "_id": "$source_type",
                    "top_news": {"$push": "$$ROOT"}
                }
            },
            {
                "$project": {
                    "top_news": {"$slice": ["$top_news", limit]}
                }
            }
        ]

        # Flatten the result into a single list
        grouped = list(self.news_collection.aggregate(pipeline))
        news = [item for group in grouped for item in group["top_news"]]
        random.shuffle(news)
        return news

    def _get_news_home(self, limit=40):

        pipeline = [
            {"$sort": {"published": -1}},  # Optional: newest first
            {
                "$group": {
                    "_id": "$source_type",
                    "top_news": {"$push": "$$ROOT"}
                }
            },
            {
                "$project": {
                    "top_news": {"$slice": ["$top_news", limit]}
                }
            }
        ]

        # Flatten the result into a single list
        grouped = list(self.news_collection.aggregate(pipeline))
        news = [item for group in grouped for item in group["top_news"]]
        random.shuffle(news)
        return news


def get_vn_express(rss_url, is_slide=False):
    # Load RSS feed
    response = requests.get(rss_url)
    soup = BeautifulSoup(response.content, "xml")

    data = []
    slide_count = 0
    max_slide_count = 10
    idx_is_long = 0
    next_is_long = 10
    # Loop through each item
    for idx, item in enumerate(soup.find_all("item")):
        title = item.title.text
        link = item.link.text.replace(vn_url, "")
        description = item.description.text

        # Extract image URL from description using BeautifulSoup again (HTML inside CDATA)
        desc_soup = BeautifulSoup(description, "html.parser")
        img_tag = desc_soup.find("img")
        image_url = img_tag["src"] if img_tag else None

        is_long = False
        if len(title) > 50:
            if idx_is_long < (idx - next_is_long):
                is_long = True
                idx_is_long = idx

        row = {
            "title": title,
            "link": link,
            "image_url": image_url,
            "source_logo_url": "logo/vne_logo_rss.png",
            "description": description,
        }
        if is_slide == False:
            row["is_long"] = is_long

        if is_slide:
            if not image_url:
                continue
            slide_count += 1
            if slide_count > max_slide_count:
                break

        data.append(row)

    return data
