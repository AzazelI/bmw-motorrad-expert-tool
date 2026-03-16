from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# LOAD DATABASE
with open("motorcycle_specs_database.json","r",encoding="utf-8") as f:
    database=json.load(f)

# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")

# SEARCH
@app.route("/search",methods=["POST"])
def search():

    query=request.json.get("query","").strip().upper()

    if not query:
        return jsonify({"error":"Empty query"})

    results=[]

    for bike in database:

        model=bike.get("model","").upper()

        # SIMPLE SEARCH (works for K63 / KA1 / models)
        if query in model:

            results.append({
                "model":bike.get("model"),
                "engine_cc":bike.get("engine_cc"),
                "power_kw":bike.get("power_kw"),
                "horsepower":bike.get("horsepower"),
                "kerb_weight_kg":bike.get("kerb_weight_kg"),
                "gross_weight_kg":bike.get("gross_weight_kg"),
                "payload_kg":bike.get("payload_kg"),
                "engine_type":bike.get("engine_type"),
                "fuel":bike.get("fuel")
            })

    if not results:
        return jsonify({"error":"Model not found"})

    return jsonify(results)

if __name__=="__main__":
    app.run(debug=True)