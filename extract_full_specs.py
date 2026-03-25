import os
import fitz
import re
import json

manual_path = r"D:\BMW_MOTORRAD_AI\BMW_MOTORRAD_MANUALS"

print("BMW MOTORRAD SPEC EXTRACTOR v13")
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

    # 🔥 SMART TYPE CODE DETECTION
    for p in parts:

        # K series (K66, K50...)
        if re.match(r"K[A-Z0-9]{2,3}", p):
            variant = p
            break

        # numeric codes (0M63USA → 0M63)
        if re.match(r"0[A-Z0-9]{3,}", p):
            variant = p[:4]
            break

        # A series (A75EURO → A75)
        if re.match(r"A[0-9]{2,}", p):
            variant = p[:3]
            break

    if variant:
        return f"{model}_{variant}"

    return model


specs = []
processed_models = set()


for root, dirs, files in os.walk(manual_path):

    for file in files:

        if not file.lower().endswith(".pdf"):
            continue

        clean_model = normalize_filename(file)

        if clean_model in processed_models:
            continue

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

            # =========================
            # ENGINE CAPACITY
            # =========================
            engine = re.search(r'(\d{3,4})\s?(cc|cm3|cm³)', text_lower)

            if not engine:
                engine = re.search(r'displacement.*?(\d{3,4})', text_lower)

            engine_cc = engine.group(1) if engine else None

            # =========================
            # POWER kW
            # =========================
            power_kw_match = re.search(r'(\d{2,3})\s?kw', text_lower)
            power_kw = power_kw_match.group(1) if power_kw_match else None

            # =========================
            # HORSEPOWER
            # =========================
            horsepower_match = re.search(r'(\d{2,3})\s?hp', text_lower)
            horsepower = int(horsepower_match.group(1)) if horsepower_match else None

            # =========================
            # KERB WEIGHT
            # =========================
            kerb_patterns = [
                r'kerb weight.*?(\d{2,3})\s?kg',
                r'weight ready to ride.*?(\d{2,3})\s?kg',
                r'road ready weight.*?(\d{2,3})\s?kg',
                r'unladen weight.*?(\d{2,3})\s?kg'
            ]

            kerb_weight = None
            for pattern in kerb_patterns:
                m = re.search(pattern, text_lower)
                if m:
                    kerb_weight = m.group(1)
                    break

            # =========================
            # GROSS WEIGHT
            # =========================
            gross_patterns = [
                r'permitted total weight.*?(\d{2,3})\s?kg',
                r'permitted gross weight.*?(\d{2,3})\s?kg',
                r'gross vehicle weight.*?(\d{2,3})\s?kg',
                r'maximum permissible weight.*?(\d{2,3})\s?kg'
            ]

            gross_weight = None
            for pattern in gross_patterns:
                m = re.search(pattern, text_lower)
                if m:
                    gross_weight = m.group(1)
                    break

            # =========================
            # PAYLOAD
            # =========================
            payload_match = re.search(r'payload.*?(\d{2,3})\s?kg', text_lower)
            payload = payload_match.group(1) if payload_match else None

            # =========================
            # ENGINE TYPE
            # =========================
            engine_type = None

            if "four-cylinder" in text_lower or "inline four" in text_lower:
                engine_type = "4-cylinder"
            elif "parallel twin" in text_lower:
                engine_type = "2-cylinder"
            elif "two-cylinder" in text_lower or "boxer" in text_lower:
                engine_type = "2-cylinder"
            elif "single-cylinder" in text_lower:
                engine_type = "single-cylinder"

            # =========================
            # FUEL
            # =========================
            fuel = "Petrol"

            if "electric motor" in text_lower or "electric drive" in text_lower:
                fuel = "Electric"

            # =========================
            # HP CALC
            # =========================
            if horsepower is None and power_kw:
                horsepower = round(int(power_kw) * 1.341)

            # =========================
            # CLEAN MODEL + TYPE
            # =========================
            model_name = clean_model
            type_code = None

            if "_" in clean_model:
                parts = clean_model.split("_")
                model_name = parts[0]
                type_code = parts[1]

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

            specs.append(data)
            processed_models.add(clean_model)

            print("Processed:", clean_model)

        except Exception as e:
            print("Error processing:", file)
            print(e)


print("\nSaving database...")

with open("motorcycle_specs_database.json", "w", encoding="utf-8") as f:
    json.dump(specs, f, indent=4)

print("Database created successfully.")
print("Total models:", len(specs))

input("Press Enter to exit...")