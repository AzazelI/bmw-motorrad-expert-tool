from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# 🔥 ახლა ყველაფერი app-შია
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "specs_database", "motorcycle_specs_database.json")

print("📂 Loading DB from:", DB_PATH)

# LOAD DATABASE
try:
    with open(DB_PATH, "r", encoding="utf-8") as f:
        database = json.load(f)
        print(f"✅ Database loaded: {len(database)} records")
except Exception as e:
    print("❌ Failed to load database:", e)
    database = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    try:
        data = request.get_json()
        query = data.get("query", "").strip().upper()

        if not query:
            return jsonify({"error": "Empty query"})

        results = []

        vin_code = None
        if len(query) >= 7:
            vin_code = query[3:7]

        for bike in database:

            model = str(bike.get("model", "")).upper()
            type_code = str(bike.get("type_code", "")).upper()
            vin_codes = [str(v).upper() for v in bike.get("vin_codes", [])]

            match = False

            if query in model:
                match = True
            elif query == type_code:
                match = True
            elif query in vin_codes:
                match = True
            elif vin_code and vin_code in vin_codes:
                match = True

            if match:
                bike_copy = bike.copy()

                if vin_code:
                    bike_copy["detected_vin"] = vin_code

                results.append(bike_copy)

        if not results:
            return jsonify({"error": "Model not found"})

        return jsonify(results)

    except Exception as e:
        print("❌ SEARCH ERROR:", e)
        return jsonify({"error": "Server error"})


if __name__ == "__main__":
    app.run(debug=True)