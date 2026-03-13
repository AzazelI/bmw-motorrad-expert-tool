import os
import fitz
import re
import json

manual_path = r"D:\BMW_MOTORRAD_AI\BMW_MOTORRAD_MANUALS"

print("BMW MOTORRAD SPEC EXTRACTOR v7")
print("--------------------------------")

def clean_text(t):
    t = t.replace("\n", " ")
    t = re.sub(r"\s+", " ", t)
    return t.lower()


def normalize_filename(filename):

    name = filename.replace(".pdf", "")

    # normalize dash format
    name = name.replace(" - ", "_")

    # remove spaces
    name = name.replace(" ", "")

    # special fixes for R1300 family
    if name.startswith("R1300R"):
        return "R1300R"

    if name.startswith("R1300RS"):
        return "R1300RS"

    if name.startswith("R1300RT"):
        return "R1300RT"

    # split normal format
    parts = name.split("_")

    model = parts[0]
    variant = parts[1] if len(parts) > 1 else ""

    # normalize adventure naming
    if "ADVENTURE" in model:
        model = model.replace("ADVENTURE", "A")

    clean_model = f"{model}_{variant}" if variant else model

    return clean_model


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

            # ENGINE CAPACITY
            engine = re.search(r'(\d{3,4})\s?(cc|cm3|cm³)', text_lower)

            if not engine:
                engine = re.search(r'displacement.*?(\d{3,4})', text_lower)

            engine_cc = engine.group(1) if engine else None


            # POWER
            power_kw_match = re.search(r'(\d{2,3})\s?kW', text)
            power_kw = power_kw_match.group(1) if power_kw_match else None


            # HORSEPOWER
            horsepower_match = re.search(r'(\d{2,3})\s?hp', text_lower)

            horsepower = int(horsepower_match.group(1)) if horsepower_match else None


            # KERB WEIGHT
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


            # GROSS WEIGHT
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


            # PAYLOAD
            payload_match = re.search(r'payload.*?(\d{2,3})\s?kg', text_lower)

            payload = payload_match.group(1) if payload_match else None


            # ENGINE TYPE
            engine_type = None

            if "four-cylinder" in text_lower or "inline four" in text_lower:
                engine_type = "4-cylinder"

            elif "two-cylinder" in text_lower or "2-cylinder" in text_lower or "boxer" in text_lower:
                engine_type = "2-cylinder"

            elif "single-cylinder" in text_lower:
                engine_type = "single-cylinder"


            # FUEL
            fuel = "Petrol"

            if "electric motor" in text_lower or "electric drive" in text_lower:
                fuel = "Electric"


            # CALCULATE HP
            if horsepower is None and power_kw:
                horsepower = round(int(power_kw) * 1.341)


            # SANITY CHECK
            try:

                if kerb_weight:

                    kw = int(kerb_weight)

                    if kw < 150 or kw > 350:
                        kerb_weight = None

                if kerb_weight and gross_weight:

                    if int(kerb_weight) >= int(gross_weight):
                        kerb_weight = None

            except:
                pass


            # SAVE DATA
            data = {

                "model": clean_model,
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


print("\nSaving database...")

with open("motorcycle_specs_database.json", "w") as f:
    json.dump(specs, f, indent=4)

print("Done.")

input("Press Enter to exit...")