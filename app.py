from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# -----------------------------
# LOAD DATABASE
# -----------------------------

with open("motorcycle_specs_database.json", "r", encoding="utf-8") as f:
    database = json.load(f)


# -----------------------------
# HOME PAGE
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# SEARCH FUNCTION
# -----------------------------

@app.route("/search", methods=["POST"])
def search():

    query = request.json.get("query", "").strip().upper()

    if not query:
        return jsonify({"error": "Empty query"})

    results = []

    for bike in database:

        model = bike.get("model", "").upper()

        parts = model.split("_")

        model_name = parts[0] if len(parts) > 0 else ""
        chassis = parts[1] if len(parts) > 1 else ""

        if query == model or query == model_name or query == chassis:

            results.append({
                "model": bike.get("model"),
                "engine_cc": bike.get("engine_cc"),
                "power_kw": bike.get("power_kw"),
                "horsepower": bike.get("horsepower"),
                "kerb_weight": bike.get("kerb_weight_kg"),
                "gross_weight": bike.get("gross_weight_kg"),
                "payload": bike.get("payload_kg"),
                "engine_type": bike.get("engine_type"),
                "fuel": bike.get("fuel")
            })

    if not results:
        return jsonify({"error": "Model not found"})

    return jsonify(results)


# -----------------------------
# RUN SERVER
# -----------------------------

if __name__ == "__main__":

    print("\nBMW MOTORRAD EXPERT WEB APP")
    print("---------------------------")
    print("Server running at:")
    print("http://127.0.0.1:5000\n")

    app.run(debug=True)