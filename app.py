from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# LOAD DATABASE
try:
    with open("motorcycle_specs_database.json", "r", encoding="utf-8") as f:
        database = json.load(f)
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

            vin_codes_raw = bike.get("vin_codes") or []
            vin_codes = [str(v).upper() for v in vin_codes_raw]

            if (
                query in model
                or query == type_code
                or (vin_code and vin_code in vin_codes)
                or query in vin_codes
            ):
                results.append(bike)

        if not results:
            return jsonify({"error": "Model not found"})

        return jsonify(results)

    except Exception as e:
        print("❌ SEARCH ERROR:", e)
        return jsonify({"error": "Server error"})


if __name__ == "__main__":
    app.run(debug=True)