import json

with open("motorcycle_specs_database.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for bike in data:
    vin = bike.get("vin")

    if isinstance(vin, str):
        bike["vin"] = [vin]

with open("fixed_database.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print("✅ Fixed!")