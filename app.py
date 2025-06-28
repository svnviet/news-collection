from flask import Flask, request, jsonify, render_template, redirect
from pymongo import MongoClient
from services import get_vn_express, get_item, get_related_items, get_related_hot_items, \
    NewsService
from sync.nld import SyncNLD
from sync.vnexpress import insert_or_get_detail

app = Flask(__name__)

# Replace with your Mongo URI (local or Atlas)
mongo_uri = "mongodb://localhost:27017"
client = MongoClient(mongo_uri)
db = client["vi"]  # Create or connect to a database
collection = db["news"]  # Create or connect to a collection
news_service = NewsService()
nld_sync = SyncNLD()


@app.route("/get", methods=["GET"])
def get_data():
    items = list(collection.find({}, {"_id": 0}))
    return jsonify(items)


@app.route("/", methods=["GET"])
def get_news():
    items, hot_news = news_service.get_news()
    category = request.args.get("the-loai")
    if category == "the-gioi":
        hot_news = get_vn_express("https://vnexpress.net/rss/the-gioi.rss", is_slide=True)
        items = get_vn_express("https://vnexpress.net/rss/the-gioi.rss")[9:]

    print(hot_news)
    return render_template(
        "index.html",
        hot_news=hot_news,
        items=items,
    )


@app.route("/<path:theloai>", methods=["GET"])
def get_news_by(theloai):
    hot_news = get_vn_express("https://vnexpress.net/rss/the-gioi.rss", is_slide=True)
    items = get_vn_express("https://vnexpress.net/rss/the-gioi.rss")[9:]
    if theloai == "the-gioi":
        hot_news = get_vn_express("https://vnexpress.net/rss/the-gioi.rss", is_slide=True)
        items = get_vn_express("https://vnexpress.net/rss/the-gioi.rss")[9:]
    print(hot_news)
    return render_template(
        "index.html",
        hot_news=hot_news,
        items=items,
    )


@app.route("/load_more", methods=["GET"])
def load_more_news():
    from sync.vnexpress import collection
    page = int(request.args.get("page", 1))
    per_page = 12

    # Get paginated data
    cursor = collection.find().sort("_id", -1).skip((page - 1) * per_page).limit(per_page)

    # Convert cursor to list of dicts (MongoDB documents aren't JSON-serializable by default)
    items = []
    for item in cursor:
        item['_id'] = str(item['_id'])  # convert ObjectId to string
        items.append(item)

    return jsonify(items)


@app.route('/vn-vi/<path:source>/<path:slug>', methods=['GET'])
def detail(slug, source):
    if not source:
        return "Missing link", 400
    print(source)
    print(slug)
    link = ""
    detail_data = None
    if source == "VNExpress":
        link = "https://vnexpress.net/" + slug
        detail_data = insert_or_get_detail(link)
    if source == "NLD":
        link = "https://nld.com.vn/" + slug
        detail_data = nld_sync.insert_or_get_detail(link)
    if not link:
        return "Missing link", 400
    if not detail_data:
        return redirect(link, code=302)

    items, hot_news = news_service.get_news()
    print(detail_data)
    return render_template("detail.html", article=detail_data, hot_news=hot_news, items=items, item=detail_data)


@app.route("/load_related", methods=["GET"])
def detail_related_news():
    # items = get_related_items()
    # hot_news = get_related_hot_items()
    # detail_news = get_item()
    # link = "https://vnexpress.net/" + detail_news['link']
    # detail_news = insert_or_get_detail(link)
    #
    # news_html = render_template("components/detail/news-feed.html",
    #                             items=items,
    #                             hot_news=hot_news, )
    # consumption_html = render_template("components/detail/consumption-feed-content.html", article_rd=detail_news, )

    return jsonify({
        "news_html": None,
        "consumption_html": None
    })


if __name__ == "__main__":
    app.run(debug=True)
