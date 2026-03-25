import json

# LOAD DATABASE
with open("motorcycle_specs_database.json", "r", encoding="utf-8") as f:
    database = json.load(f)


def search_bike(query):
    query = query.strip().upper()

    if not query:
        print("❌ Empty input")
        return

    results = []

    # 🔥 FULL VIN SUPPORT
    vin_code = None
    if len(query) >= 7:
        vin_code = query[3:7]

    for bike in database:

        model = bike.get("model", "").upper()
        type_code = bike.get("type_code", "").upper()
        vin_codes = [v.upper() for v in bike.get("vin_codes", [])]

        if (
            query in model
            or query == type_code
            or (vin_code and vin_code in vin_codes)
            or query in vin_codes
        ):
            results.append(bike)

    if not results:
        print("❌ Model not found")
        return

    # PRINT RESULTS
    for bike in results:
        print("\n==============================")
        print(f"🏍 Model: {bike.get('model')}")
        print(f"🔧 Type Code: {bike.get('type_code')}")
        print(f"📄 Manual: {bike.get('source_file')}")

        print("\n--- Specs ---")

        print(f"Engine: {bike.get('engine_cc')} cc")
        print(f"Power: {bike.get('power_kw')} kW")
        print(f"Horsepower: {bike.get('horsepower')} hp")
        print(f"Weight: {bike.get('kerb_weight_kg')} kg")
        print(f"Fuel: {bike.get('fuel')}")
        print("==============================\n")


# CLI LOOP
if __name__ == "__main__":
    print("BMW Motorrad CLI Tool")
    print("Type model, type code, or VIN (full or 4-digit)\n")

    while True:
        user_input = input("Search: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        search_bike(user_input)