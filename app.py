from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# 🔥 Paths
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
        query = str(data.get("query", "")).strip().upper()

        if not query:
            return jsonify({"error": "Empty query"})

        results = []

        # 🔥 Extract VIN code (4–7)
        vin_code = query[3:7] if len(query) >= 7 else query

        for bike in database:

            model = str(bike.get("model", "")).upper()
            type_code = str(bike.get("type_code", "")).upper()

            # 🔥 GET VIN DATA (supports old + new)
            vin_data = bike.get("vin", bike.get("vin_codes", []))

            # normalize to list
            if isinstance(vin_data, str):
                vin_list = [vin_data.strip().upper()]
            elif isinstance(vin_data, list):
                vin_list = [str(v).strip().upper() for v in vin_data]
            else:
                vin_list = []

            match = False

            # =========================
            # 🔍 SEARCH LOGIC
            # =========================

            # MODEL
            if query in model:
                match = True

            # TYPE CODE
            elif query == type_code:
                match = True

            # EXACT VIN MATCH
            elif query in vin_list:
                match = True

            # EXTRACTED VIN MATCH
            elif vin_code in vin_list:
                match = True

            # 🔥 ADVANCED VIN MATCH (fix for 0E63 issue)
            else:
                for v in vin_list:

                    # remove spaces just in case
                    v_clean = v.replace(" ", "")
                    vc_clean = vin_code.replace(" ", "")

                    # exact
                    if vc_clean == v_clean:
                        match = True
                        break

                    # shift fix (0E63 vs E630)
                    if vc_clean.replace("0", "") == v_clean.replace("0", ""):
                        match = True
                        break

                    # partial safety
                    if vc_clean in v_clean or v_clean in vc_clean:
                        match = True
                        break

            # =========================

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