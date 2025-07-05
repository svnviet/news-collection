from flask import Flask, request, jsonify, render_template, redirect
from services import get_vn_express, NewsService
from settings.db import client

app = Flask(__name__)

# Replace with your Mongo URI (local or Atlas)
db = client["vn-news"]  # Create or connect to a database
collection = db["news"]  # Create or connect to a collection
news_service = NewsService()


@app.route("/", methods=["GET"])
def get_news():
    items, hot_news = news_service.get_news()
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
    page = int(request.args.get("page", 1)) + 80 // 12
    per_page = 12

    items = news_service.load_more_news(page, per_page)

    return jsonify(items)


@app.route('/vn-vi/<path:source>/<path:slug>', methods=['GET'])
def detail(slug, source):
    if not source:
        return "Missing link", 400
    try:
        link, detail_data = news_service.get_detail(slug, source)
    except Exception:
        return "Missing link", 400
    if not link:
        return "Missing link", 400
    if not detail_data:
        return redirect(link, code=302)

    items, hot_news = news_service.get_news()
    return render_template("detail.html", article=detail_data, hot_news=hot_news, items=items, item=detail_data)


@app.route("/load_related", methods=["GET"])
def detail_related_news():
    page = int(request.args.get("page", 1)) + 1
    per_page = 20

    items, hot_news, item = news_service.get_news_related(page, per_page)

    news_html = render_template(
        "components/detail/news-feed.html",
        items=items,
        hot_news=hot_news,
    )
    consumption_html = render_template("components/detail/consumption-feed-content.html", article_rd=item, )

    return jsonify({
        "news_html": news_html,
        "consumption_html": consumption_html
    })


if __name__ == "__main__":
    app.run(debug=True)
