import os
from supabase import create_client, Client

# შენი ლოკალური სკრიპტისთვის პირდაპირ ვიყენებთ გასაღებებს
SUPABASE_URL = "https://xxtwhxvafgkdrtuqqetu.supabase.co"
SUPABASE_KEY = "sb_publishable_js3pEbUOHt__E9EBIoSYfQ_5qVCBImI"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 30 ახალი BMW მოტოციკლის გამზადებული ბაზა
new_bikes = [
    {"model": "M 1000 RR", "type_code": "0P01", "engine_cc": "999", "power_kw": "156", "horsepower": "212", "kerb_weight_kg": "193", "gross_weight_kg": "407", "payload_kg": "214", "engine_type": "Inline-4", "fuel": "Petrol", "vins": ["0P01"], "sources": []},
    {"model": "M 1000 R", "type_code": "0P11", "engine_cc": "999", "power_kw": "154", "horsepower": "210", "kerb_weight_kg": "199", "gross_weight_kg": "407", "payload_kg": "208", "engine_type": "Inline-4", "fuel": "Petrol", "vins": ["0P11"], "sources": []},
    {"model": "S 1000 RR", "type_code": "0E61", "engine_cc": "999", "power_kw": "154", "horsepower": "210", "kerb_weight_kg": "197", "gross_weight_kg": "407", "payload_kg": "210", "engine_type": "Inline-4", "fuel": "Petrol", "vins": ["0E61"], "sources": []},
    {"model": "S 1000 R", "type_code": "0E51", "engine_cc": "999", "power_kw": "121", "horsepower": "165", "kerb_weight_kg": "199", "gross_weight_kg": "407", "payload_kg": "208", "engine_type": "Inline-4", "fuel": "Petrol", "vins": ["0E51"], "sources": []},
    {"model": "S 1000 XR", "type_code": "0E41", "engine_cc": "999", "power_kw": "125", "horsepower": "170", "kerb_weight_kg": "227", "gross_weight_kg": "450", "payload_kg": "223", "engine_type": "Inline-4", "fuel": "Petrol", "vins": ["0E41"], "sources": []},
    
    {"model": "R 1300 GS", "type_code": "0M21", "engine_cc": "1300", "power_kw": "107", "horsepower": "145", "kerb_weight_kg": "237", "gross_weight_kg": "465", "payload_kg": "228", "engine_type": "Boxer", "fuel": "Petrol", "vins": ["0M21"], "sources": []},
    {"model": "R 1300 GS Adventure", "type_code": "0M23", "engine_cc": "1300", "power_kw": "107", "horsepower": "145", "kerb_weight_kg": "269", "gross_weight_kg": "485", "payload_kg": "216", "engine_type": "Boxer", "fuel": "Petrol", "vins": ["0M23"], "sources": []},
    {"model": "R 1250 RT", "type_code": "0J61", "engine_cc": "1254", "power_kw": "100", "horsepower": "136", "kerb_weight_kg": "279", "gross_weight_kg": "505", "payload_kg": "226", "engine_type": "Boxer", "fuel": "Petrol", "vins": ["0J61"], "sources": []},
    {"model": "R 1250 R", "type_code": "0J71", "engine_cc": "1254", "power_kw": "100", "horsepower": "136", "kerb_weight_kg": "239", "gross_weight_kg": "460", "payload_kg": "221", "engine_type": "Boxer", "fuel": "Petrol", "vins": ["0J71"], "sources": []},
    {"model": "R 1250 RS", "type_code": "0J81", "engine_cc": "1254", "power_kw": "100", "horsepower": "136", "kerb_weight_kg": "243", "gross_weight_kg": "460", "payload_kg": "217", "engine_type": "Boxer", "fuel": "Petrol", "vins": ["0J81"], "sources": []},
    
    {"model": "F 900 GS", "type_code": "0B01", "engine_cc": "895", "power_kw": "77", "horsepower": "105", "kerb_weight_kg": "219", "gross_weight_kg": "445", "payload_kg": "226", "engine_type": "Inline-2", "fuel": "Petrol", "vins": ["0B01"], "sources": []},
    {"model": "F 900 GS Adventure", "type_code": "0B11", "engine_cc": "895", "power_kw": "77", "horsepower": "105", "kerb_weight_kg": "246", "gross_weight_kg": "455", "payload_kg": "209", "engine_type": "Inline-2", "fuel": "Petrol", "vins": ["0B11"], "sources": []},
    {"model": "F 800 GS", "type_code": "0B21", "engine_cc": "895", "power_kw": "64", "horsepower": "87", "kerb_weight_kg": "227", "gross_weight_kg": "440", "payload_kg": "213", "engine_type": "Inline-2", "fuel": "Petrol", "vins": ["0B21"], "sources": []},
    
    {"model": "R 18", "type_code": "0L11", "engine_cc": "1802", "power_kw": "67", "horsepower": "91", "kerb_weight_kg": "345", "gross_weight_kg": "560", "payload_kg": "215", "engine_type": "Boxer", "fuel": "Petrol", "vins": ["0L11"], "sources": []},
    {"model": "R 18 Classic", "type_code": "0L21", "engine_cc": "1802", "power_kw": "67", "horsepower": "91", "kerb_weight_kg": "365", "gross_weight_kg": "560", "payload_kg": "195", "engine_type": "Boxer", "fuel": "Petrol", "vins": ["0L21"], "sources": []},
    {"model": "R 18 Transcontinental", "type_code": "0L31", "engine_cc": "1802", "power_kw": "67", "horsepower": "91", "kerb_weight_kg": "427", "gross_weight_kg": "630", "payload_kg": "203", "engine_type": "Boxer", "fuel": "Petrol", "vins": ["0L31"], "sources": []},
    {"model": "R 18 Roctane", "type_code": "0L41", "engine_cc": "1802", "power_kw": "67", "horsepower": "91", "kerb_weight_kg": "374", "gross_weight_kg": "560", "payload_kg": "186", "engine_type": "Boxer", "fuel": "Petrol", "vins": ["0L41"], "sources": []},
    
    {"model": "R 12 nineT", "type_code": "0N11", "engine_cc": "1170", "power_kw": "80", "horsepower": "109", "kerb_weight_kg": "220", "gross_weight_kg": "430", "payload_kg": "210", "engine_type": "Boxer", "fuel": "Petrol", "vins": ["0N11"], "sources": []},
    {"model": "R 12", "type_code": "0N01", "engine_cc": "1170", "power_kw": "70", "horsepower": "95", "kerb_weight_kg": "227", "gross_weight_kg": "430", "payload_kg": "203", "engine_type": "Boxer", "fuel": "Petrol", "vins": ["0N01"], "sources": []},
    
    {"model": "K 1600 GT", "type_code": "0F01", "engine_cc": "1649", "power_kw": "118", "horsepower": "160", "kerb_weight_kg": "343", "gross_weight_kg": "540", "payload_kg": "197", "engine_type": "Inline-6", "fuel": "Petrol", "vins": ["0F01"], "sources": []},
    {"model": "K 1600 GTL", "type_code": "0F11", "engine_cc": "1649", "power_kw": "118", "horsepower": "160", "kerb_weight_kg": "358", "gross_weight_kg": "560", "payload_kg": "202", "engine_type": "Inline-6", "fuel": "Petrol", "vins": ["0F11"], "sources": []},
    {"model": "K 1600 B", "type_code": "0F21", "engine_cc": "1649", "power_kw": "118", "horsepower": "160", "kerb_weight_kg": "344", "gross_weight_kg": "560", "payload_kg": "216", "engine_type": "Inline-6", "fuel": "Petrol", "vins": ["0F21"], "sources": []},
    {"model": "K 1600 Grand America", "type_code": "0F31", "engine_cc": "1649", "power_kw": "118", "horsepower": "160", "kerb_weight_kg": "367", "gross_weight_kg": "560", "payload_kg": "193", "engine_type": "Inline-6", "fuel": "Petrol", "vins": ["0F31"], "sources": []},
    
    {"model": "CE 04", "type_code": "0C51", "engine_cc": "0", "power_kw": "31", "horsepower": "42", "kerb_weight_kg": "231", "gross_weight_kg": "410", "payload_kg": "179", "engine_type": "Electric", "fuel": "Electric", "vins": ["0C51"], "sources": []},
    {"model": "CE 02", "type_code": "0C71", "engine_cc": "0", "power_kw": "11", "horsepower": "15", "kerb_weight_kg": "132", "gross_weight_kg": "312", "payload_kg": "180", "engine_type": "Electric", "fuel": "Electric", "vins": ["0C71"], "sources": []},
    
    {"model": "C 400 X", "type_code": "0C09", "engine_cc": "350", "power_kw": "25", "horsepower": "34", "kerb_weight_kg": "206", "gross_weight_kg": "405", "payload_kg": "199", "engine_type": "Single-Cylinder", "fuel": "Petrol", "vins": ["0C09"], "sources": []},
    {"model": "C 400 GT", "type_code": "0C06", "engine_cc": "350", "power_kw": "25", "horsepower": "34", "kerb_weight_kg": "214", "gross_weight_kg": "415", "payload_kg": "201", "engine_type": "Single-Cylinder", "fuel": "Petrol", "vins": ["0C06"], "sources": []},
    
    {"model": "G 310 GS", "type_code": "0G12", "engine_cc": "313", "power_kw": "25", "horsepower": "34", "kerb_weight_kg": "175", "gross_weight_kg": "345", "payload_kg": "170", "engine_type": "Single-Cylinder", "fuel": "Petrol", "vins": ["0G12"], "sources": []},
    {"model": "G 310 R", "type_code": "0G11", "engine_cc": "313", "power_kw": "25", "horsepower": "34", "kerb_weight_kg": "164", "gross_weight_kg": "345", "payload_kg": "181", "engine_type": "Single-Cylinder", "fuel": "Petrol", "vins": ["0G11"], "sources": []},
    {"model": "G 310 RR", "type_code": "0G21", "engine_cc": "313", "power_kw": "25", "horsepower": "34", "kerb_weight_kg": "174", "gross_weight_kg": "345", "payload_kg": "171", "engine_type": "Single-Cylinder", "fuel": "Petrol", "vins": ["0G21"], "sources": []}
]

try:
    print(f"🔄 ვიწყებ {len(new_bikes)} მოტოციკლის ატვირთვას...")
    # მონაცემების პირდაპირ ბაზაში გაშვება
    response = supabase.table("motorcycles").insert(new_bikes).execute()
    print("✅ 30-ივე მოტოციკლი წარმატებით დაემატა Supabase-ში!")
except Exception as e:
    print(f"❌ შეცდომა ატვირთვისას: {e}")