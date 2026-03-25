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

        # 🔥 detect VIN
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

                # 🔥 attach detected VIN code
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