import json

print("\nBMW MOTORRAD EXPERT TOOL")
print("------------------------")

search = input("Enter chassis code OR model (example: K67 or S1000RR): ").strip().upper()

with open("motorcycle_specs_database.json","r") as f:
    data = json.load(f)

results = []

for item in data:

    model = item.get("model","").upper()

    if search in model:
        results.append(item)

if not results:

    print("\nModel not found in database.")

else:

    for found in results:

        print("\n==============================")
        print("MODEL:", found.get("model"))

        print("\n--- TECHNICAL DATA ---")

        print("Engine capacity:", found.get("engine_cc"),"cc")
        print("Power:", found.get("power_kw"),"kW")
        print("Horsepower:", found.get("horsepower"),"hp")
        print("Kerb weight:", found.get("kerb_weight_kg"),"kg")
        print("Gross weight:", found.get("gross_weight_kg"),"kg")
        print("Payload:", found.get("payload_kg"),"kg")
        print("Engine type:", found.get("engine_type"))
        print("Fuel:", found.get("fuel"))

input("\nPress Enter to exit...")