from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from services import get_vn_express, get_article_detail

app = Flask(__name__)

# Replace with your Mongo URI (local or Atlas)
mongo_uri = "mongodb://localhost:27017"
client = MongoClient(mongo_uri)
db = client["vi"]  # Create or connect to a database
collection = db["news"]  # Create or connect to a collection


@app.route("/add", methods=["POST"])
def add_data():
    data = request.get_json()
    result = collection.insert_one(data)
    return jsonify({"inserted_id": str(result.inserted_id)})


@app.route("/get", methods=["GET"])
def get_data():
    items = list(collection.find({}, {"_id": 0}))
    return jsonify(items)


@app.route("/", methods=["GET"])
def get_news():
    hot_news = get_vn_express("https://vnexpress.net/rss/thoi-su.rss", is_slide=True)
    items = get_vn_express("https://vnexpress.net/rss/thoi-su.rss")[9:]
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
    page = int(request.args.get("page", 1))
    per_page = 4
    all_items = get_vn_express("https://vnexpress.net/rss/tin-noi-bat.rss")
    items = all_items[(page - 1) * per_page: page * per_page]

    return jsonify(items)


@app.route('/vn-vi/news/<path:slug>', methods=['GET'])
def detail(slug):
    link = "https://vnexpress.net/" + slug
    if not link:
        return "Missing link", 400
    # Parse the article detail (you'll need a parser here)
    detail_data = get_article_detail(link)
    detail_data["article_url"] = link

    item = get_vn_express("https://vnexpress.net/rss/tin-moi-nhat.rss")[1]
    return render_template("detail.html", article=detail_data, item=item)


if __name__ == "__main__":
    app.run(debug=True)
