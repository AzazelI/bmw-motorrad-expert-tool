import json

print("\nBMW MOTORRAD EXPERT TOOL")
print("------------------------")

search = input("Enter chassis code OR model (example: K67 or S1000RR): ").upper()

with open("motorcycle_specs_database.json","r") as f:
    data = json.load(f)

found = None

for item in data:

    file_name = item.get("file","").upper()
    model = item.get("model","").upper()

    if search in file_name or search in model:
        found = item
        break

if not found:

    print("\nModel not found in database.")

else:

    print("\nMODEL FILE:", found.get("file"))

    engine = found.get("engine_cc")
    power_kw = found.get("power_kw")
    hp = found.get("horsepower")
    kerb = found.get("kerb_weight_kg")
    gross = found.get("gross_weight_kg")
    engine_type = found.get("engine_type")
    fuel = found.get("fuel")

    print("\n--- TECHNICAL DATA ---")

    if engine:
        print("Engine capacity:", engine,"cc")

    if power_kw:
        print("Power:", power_kw,"kW")

    if hp:
        print("Horsepower:", hp,"hp")

    if kerb:
        print("Kerb weight:", kerb,"kg")

    if gross:
        print("Gross weight:", gross,"kg")

    if engine_type:
        print("Engine type:", engine_type)

    if fuel:
        print("Fuel:", fuel)

input("\nPress Enter to exit...")