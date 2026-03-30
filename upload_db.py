import json
from supabase import create_client, Client

# შენი Supabase მონაცემები
SUPABASE_URL = "https://xxtwhxvafgkdrtuqqetu.supabase.co"
SUPABASE_KEY = "sb_publishable_js3pEbUOHt__E9EBIoSYfQ_5qVCBImI" 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# JSON ფაილის წაკითხვა (დარწმუნდი რომ ფაილის სახელი სწორია)
file_path = "specs_database/motorcycle_specs_database.json"
# თუ specs_database ფოლდერში გაქვს, მაშინ დაწერე: "specs_database/motorcycle_specs_database.json"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        bikes_data = json.load(f)
        print(f"✅ წაკითხულია {len(bikes_data)} მოტოციკლი. ვიწყებ ატვირთვას...")

    # Supabase-ში ატვირთვა
    response = supabase.table("motorcycles").insert(bikes_data).execute()
    print("🚀 მონაცემები წარმატებით აიტვირთა Supabase-ში!")

except Exception as e:
    print(f"❌ შეცდომა: {e}")