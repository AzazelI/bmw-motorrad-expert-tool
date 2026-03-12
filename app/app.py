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

    query = request.json.get("query", "").upper()

    for bike in database:

        file_name = bike.get("file", "").upper()
        model = bike.get("model", "").upper()

        if query in file_name or query in model:

            return jsonify({
                "file": bike.get("file"),
                "engine_cc": bike.get("engine_cc"),
                "power_kw": bike.get("power_kw"),
                "horsepower": bike.get("horsepower"),
                "kerb_weight": bike.get("kerb_weight_kg"),
                "gross_weight": bike.get("gross_weight_kg"),
                "engine_type": bike.get("engine_type"),
                "fuel": bike.get("fuel")
            })

    return jsonify({"error": "Model not found"})


# -----------------------------
# RUN SERVER
# -----------------------------

if __name__ == "__main__":

    print("\nBMW MOTORRAD EXPERT WEB APP")
    print("---------------------------")
    print("Server running at:")
    print("http://127.0.0.1:5000\n")


    app.run(debug=True)

