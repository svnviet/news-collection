import os

from flask import render_template, Blueprint, request, redirect, send_from_directory

from app import db
from app.config import Config

home_bp = Blueprint("home", __name__)


def get_video_by_id(video_id="2802"):
    """Fetch a video by ID"""
    return db.db.movies.find_one({"movie_id": int(video_id)})


def get_related_videos(video):
    """Fetch related videos based on related_videos list"""
    return list(db.db.movies.aggregate([
        {"$match": {"categories": video["categories"][0], "movie_id": {"$ne": video["movie_id"]}}},
        # Filter category & exclude movie_id
        {"$sample": {"size": 15}}  # Randomly select 15 movies
    ]))


# Expanded search history (30 items)
search_hs = ["Sinh Con", "Khong Che", "Chi Dau", "Dit Ban Than", "Me Cua Thang Ban Ban Than", "Loan Luan", "Sep Nu",
             "Me Con Dam Loan", "Trung So", "Thuoc Kich Duc", "Nguoi Yeu Cu",
             "Rina Ishihara", "Akiho", "Yoshizawa", "Kotomi", "Yuzuno", "Xuat Tinh Day Lon", "Doi Vo",
             "Con Oi", "Me Nung Qua", "Hikari Kisaki", "Me Co", "Loan Luan", "Me Va Con", "Du Di", "Rin Yamamoto",
             "Chu Tro",
             "Minami Aizawa", "Vu To", "Me Oi Con Muon", "Me Ke", "Sex", "Dit Gai", "Mup Xinh Trang Non", "Khong Che",
             "ROYD 132"]
search_history = [
    {"name": f"{i}", "search": f"{i.replace(" ", "-").lower()}"} for i in search_hs
]


@home_bp.route("/")
@home_bp.route("/vlxx")
def home():
    url = request.url
    page = request.args.get("page", 1, type=int)
    category = request.args.get("theloai", None, type=str)
    search = request.args.get("timkiem", None, type=str)
    actress = request.args.get("actress", None, type=str)
    per_page = 30

    # Build MongoDB query
    query = {}
    if category:
        query.update({"categories": category})

    if search:
        normalized_search = normalize_text(search)
        query.update({"search_key": {"$regex": normalized_search, "$options": "i"}})

    if actress:
        query.update({"actress": actress})

    total_videos = db.db.movies.count_documents(query)
    if category == 'Phim hay':
        videos_cursor = (
            db.db.movies.find()
            .sort("internal_views", -1)  # Sort by more views first
            .skip((page - 1) * per_page)
            .limit(per_page)
        )
    else:
        videos_cursor = (
            db.db.movies.find(query)
            # .sort("created_at", -1)  # Sort by newest first
            .sort("movie_id", -1)  # Sort by newest first
            .skip((page - 1) * per_page)
            .limit(per_page)
        )

    paginated_videos = [{**v, "_id": str(v["_id"])} for v in videos_cursor]  # Convert _id to string
    total_pages = (total_videos + per_page - 1) // per_page

    page_numbers = {1, 2, total_pages - 1, total_pages}  # Always show first & last 2 pages
    page_numbers.update(range(page - 2, page + 3))  # Show current page ±2
    page_numbers = sorted(p for p in page_numbers if 1 <= p <= total_pages)  # Remove invalid pages
    print(total_pages)
    return render_template(
        "index.html",
        videos=paginated_videos,
        total_pages=total_pages,
        current_page=page,
        page_numbers=page_numbers,
        selected_category=category if category else None,
        search_history=search_history,  # Pass search history
        url=url,
    )


@home_bp.route("/video/<slug>/<int:movie_id>")
def watch_video(slug, movie_id):
    movie_id = str(movie_id)
    video = get_video_by_id(movie_id)
    views = video.get("internal_views", 0) + 1
    db.db.movies.update_one(
        {"movie_id": movie_id},
        {"$set": {"internal_views": views}}
    )
    if video:
        related_videos = get_related_videos(video)
        return render_template("watch.html",
                               video=video,
                               related_videos=related_videos,
                               # categories=categories,  # Pass categories
                               search_history=search_history,  # Pass search history
                               url=request.url
                               )
    return redirect(Config.BASE_URL)


@home_bp.errorhandler(404)
def page_not_found(e):
    return redirect(Config.BASE_URL)


@home_bp.route("/robots.txt")
def robots():
    return send_from_directory(os.path.join(Config.BASE_DIR, 'templates'), "robots.txt", mimetype='text/plain')


@home_bp.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(Config.BASE_DIR, 'templates'), 'sitemap.xml', mimetype='application/xml')
