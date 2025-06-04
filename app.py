from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from services import get_vn_express, get_article_detail, get_items, get_item, get_related_items, get_related_hot_items

app = Flask(__name__)

# Replace with your Mongo URI (local or Atlas)
mongo_uri = "mongodb://localhost:27017"
client = MongoClient(mongo_uri)
db = client["vi"]  # Create or connect to a database
collection = db["news"]  # Create or connect to a collection


@app.route("/get", methods=["GET"])
def get_data():
    items = list(collection.find({}, {"_id": 0}))
    return jsonify(items)


@app.route("/", methods=["GET"])
def get_news():
    hot_news = get_vn_express("https://vnexpress.net/rss/thoi-su.rss", is_slide=True)
    items = get_vn_express("https://vnexpress.net/rss/tin-moi-nhat.rss")[9:]
    category = request.args.get("the-loai")
    if category == "the-gioi":
        hot_news = get_vn_express("https://vnexpress.net/rss/the-gioi.rss", is_slide=True)
        items = get_vn_express("https://vnexpress.net/rss/the-gioi.rss")[9:]

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


@app.route('/vn-vi/news/<path:slug>', methods=['GET'])
def detail(slug):
    link = "https://vnexpress.net/" + slug
    if not link:
        return "Missing link", 400
    from sync.vnexpress import insert_or_get_detail
    detail_data = insert_or_get_detail(link)
    item = get_vn_express("https://vnexpress.net/rss/tin-moi-nhat.rss")[1]
    items = get_items()
    hot_news = get_vn_express("https://vnexpress.net/rss/thoi-su.rss", is_slide=True)
    return render_template("detail.html", article=detail_data, hot_news=hot_news, items=items, item=item)


@app.route("/load_related", methods=["GET"])
def detail_related_news():
    items = get_related_items()
    hot_news = get_related_hot_items()
    detail_news = get_item()
    from sync.vnexpress import insert_or_get_detail
    link = "https://vnexpress.net/" + detail_news['link']
    detail_news = insert_or_get_detail(link)

    news_html = render_template("components/detail/news-feed.html",
                                items=items,
                                hot_news=hot_news, )
    consumption_html = render_template("components/detail/consumption-feed-content.html", article_rd=detail_news, )

    return jsonify({
        "news_html": news_html,
        "consumption_html": consumption_html
    })


if __name__ == "__main__":
    app.run(debug=True)
