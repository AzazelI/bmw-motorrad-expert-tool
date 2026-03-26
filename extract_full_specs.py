import os
import fitz
import re
import json

manual_path = r"D:\BMW_MOTORRAD_AI\BMW_MOTORRAD_MANUALS"
db_path = r"D:\BMW_MOTORRAD_AI\app\specs_database\motorcycle_specs_database.json"

print("BMW MOTORRAD SAFE EXTRACTOR v2")
print("--------------------------------")


def clean_text(t):
    t = t.replace("\n", " ")
    t = re.sub(r"\s+", " ", t)
    return t.lower()


def normalize_filename(filename):
    name = filename.replace(".pdf", "")
    name = name.replace(" - ", "_")
    name = name.replace(" ", "")
    name = name.upper()

    parts = name.split("_")

    model = parts[0]
    variant = None

    for p in parts:
        if re.match(r"K[A-Z0-9]{2,3}", p):
            variant = p
            break
        if re.match(r"0[A-Z0-9]{3,}", p):
            variant = p[:4]
            break
        if re.match(r"A[0-9]{2,}", p):
            variant = p[:3]
            break

    if variant:
        return model, variant

    return model, None


# =========================
# LOAD EXISTING DATABASE
# =========================
existing_db = []

if os.path.exists(db_path):
    with open(db_path, "r", encoding="utf-8") as f:
        try:
            existing_db = json.load(f)
            print(f"✅ Loaded existing DB: {len(existing_db)} records")
        except:
            print("⚠️ Existing DB corrupted, starting fresh")

# Create lookup map
existing_map = {}

for bike in existing_db:
    key = f"{bike.get('model')}_{bike.get('type_code')}"
    existing_map[key] = bike


# =========================
# PROCESS FILES
# =========================
new_map = {}

for root, dirs, files in os.walk(manual_path):
    for file in files:

        if not file.lower().endswith(".pdf"):
            continue

        model_name, type_code = normalize_filename(file)
        key = f"{model_name}_{type_code}"

        path = os.path.join(root, file)

        try:
            doc = fitz.open(path)

            text = ""
            for page in doc:
                try:
                    text += page.get_text()
                except:
                    pass

            text_lower = clean_text(text)

            # ENGINE
            engine = re.search(r'(\d{3,4})\s?(cc|cm3|cm³)', text_lower)
            if not engine:
                engine = re.search(r'displacement.*?(\d{3,4})', text_lower)
            engine_cc = engine.group(1) if engine else None

            # POWER
            power_kw_match = re.search(r'(\d{2,3})\s?kw', text_lower)
            power_kw = power_kw_match.group(1) if power_kw_match else None

            # HP
            horsepower_match = re.search(r'(\d{2,3})\s?hp', text_lower)
            horsepower = int(horsepower_match.group(1)) if horsepower_match else None

            # KERB
            kerb_patterns = [
                r'kerb weight.*?(\d{2,3})\s?kg',
                r'weight ready to ride.*?(\d{2,3})\s?kg'
            ]
            kerb_weight = None
            for p in kerb_patterns:
                m = re.search(p, text_lower)
                if m:
                    kerb_weight = m.group(1)
                    break

            # GROSS
            gross_patterns = [
                r'permitted total weight.*?(\d{2,3})\s?kg',
                r'gross vehicle weight.*?(\d{2,3})\s?kg'
            ]
            gross_weight = None
            for p in gross_patterns:
                m = re.search(p, text_lower)
                if m:
                    gross_weight = m.group(1)
                    break

            # PAYLOAD
            payload_match = re.search(r'payload.*?(\d{2,3})\s?kg', text_lower)
            payload = payload_match.group(1) if payload_match else None

            # ENGINE TYPE
            engine_type = None
            if "four-cylinder" in text_lower:
                engine_type = "4-cylinder"
            elif "two-cylinder" in text_lower or "boxer" in text_lower:
                engine_type = "2-cylinder"
            elif "single-cylinder" in text_lower:
                engine_type = "single-cylinder"

            # FUEL
            fuel = "Electric" if "electric" in text_lower else "Petrol"

            # HP fallback
            if horsepower is None and power_kw:
                horsepower = round(int(power_kw) * 1.341)

            data = {
                "model": model_name,
                "type_code": type_code,
                "source_file": file,
                "engine_cc": engine_cc,
                "power_kw": power_kw,
                "horsepower": horsepower,
                "kerb_weight_kg": kerb_weight,
                "gross_weight_kg": gross_weight,
                "payload_kg": payload,
                "engine_type": engine_type,
                "fuel": fuel
            }

            # 🔥 MERGE VIN
            if key in existing_map:
                old = existing_map[key]

                if "vin" in old:
                    data["vin"] = old["vin"]

            new_map[key] = data

            print("Processed:", key)

        except Exception as e:
            print("Error:", file, e)


# =========================
# MERGE OLD + NEW
# =========================
final_map = existing_map.copy()

# update with new data
final_map.update(new_map)

final_list = list(final_map.values())

# =========================
# SAVE
# =========================
with open(db_path, "w", encoding="utf-8") as f:
    json.dump(final_list, f, indent=4)

print("\n✅ SAFE DATABASE UPDATED")
print("Total records:", len(final_list))

input("Press Enter to exit...")