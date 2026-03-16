from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

with open("motorcycle_specs_database.json", "r", encoding="utf-8") as f:
    database = json.load(f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query", "").strip().upper()
    results = []

    for bike in database:
        model = bike.get("model", "").upper()
        if query in model:
            results.append(bike)

    if not results:
        return jsonify({"error": "Model not found"})

    return jsonify(results)

@app.route("/docs")
def docs():
    return render_template("docs.html")

@app.route("/support")
def support():
    return render_template("support.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
