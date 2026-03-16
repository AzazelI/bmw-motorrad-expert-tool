import json

print("\nBMW MOTORRAD EXPERT TOOL")
print("------------------------")

search = input("Enter chassis code OR model (example: K67 or S1000RR): ").strip().upper()

with open("motorcycle_specs_database.json", "r") as f:
    data = json.load(f)

results = []

for item in data:

    model = item.get("model", "").upper()

    parts = model.split("_")

    model_name = parts[0] if len(parts) > 0 else ""
    chassis = parts[1] if len(parts) > 1 else ""

    if search == model_name or search == chassis or search == model:
        results.append(item)


if not results:

    print("\nModel not found in database.")

else:

    if len(results) > 1 and search.startswith("K"):
        print(f"\nChassis {search} is used by multiple BMW Motorrad models:")

    for found in results:

        print("\n==============================")

        print("MODEL:", found.get("model"))
        print("SOURCE FILE:", found.get("source_file"))

        engine = found.get("engine_cc")
        power_kw = found.get("power_kw")
        hp = found.get("horsepower")
        kerb = found.get("kerb_weight_kg")
        gross = found.get("gross_weight_kg")
        payload = found.get("payload_kg")
        engine_type = found.get("engine_type")
        fuel = found.get("fuel")

        print("\n--- TECHNICAL DATA ---")

        if engine:
            print("Engine capacity:", engine, "cc")

        if power_kw:
            print("Power:", power_kw, "kW")

        if hp:
            print("Horsepower:", hp, "hp")

        if kerb:
            print("Kerb weight:", kerb, "kg")

        if gross:
            print("Gross weight:", gross, "kg")

        if payload:
            print("Payload:", payload, "kg")

        if engine_type:
            print("Engine type:", engine_type)

        if fuel:
            print("Fuel:", fuel)

input("\nPress Enter to exit...")