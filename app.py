from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from services import get_vn_express

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
    items = get_vn_express()
    return render_template(
        "index.html",
        items=items
    )


if __name__ == "__main__":
    app.run(debug=True)
