import os

from flask import Flask, request, jsonify, render_template, redirect, send_from_directory, url_for
from services import get_vn_express, NewsService
from settings import Config
from settings.db import client
from flask import Response
from datetime import datetime

config = Config()
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


@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    pages = []

    # Static URLs
    ten_days_ago = datetime.now().date().isoformat()
    pages.append({
        "loc": url_for('get_news', _external=True),
        "lastmod": ten_days_ago
    })

    for post in news_service.get_all_news():  # Define this based on your DB
        pages.append({
            "loc": f"https://tin360.info/vn-vi/{post['source_type']}/{post['link']}",
            "lastmod": post.get("published", ten_days_ago)
        })

    sitemap_xml = render_template("sitemap_template.xml", pages=pages)
    return Response(sitemap_xml, mimetype="application/xml")


@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')


if __name__ == "__main__":
    app.run(debug=True)
