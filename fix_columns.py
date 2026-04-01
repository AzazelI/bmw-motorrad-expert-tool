import os
from supabase import create_client, Client

SUPABASE_URL = "https://xxtwhxvafgkdrtuqqetu.supabase.co"
SUPABASE_KEY = "sb_publishable_js3pEbUOHt__E9EBIoSYfQ_5qVCBImI"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 ვიწყებ ბაზის სკანირებას არეულ სვეტებზე...")

try:
    response = supabase.table("motorcycles").select("*").execute()
    bikes = response.data
    fixed_count = 0

    for bike in bikes:
        t_code = str(bike.get("type_code", "")).strip()
        v_ins = bike.get("vins", [])

        needs_update = False
        new_type_code = t_code
        new_vins = v_ins

        # ვამოწმებთ, ხომ არ წერია type_code-ში სია (მაგ: '["0M21"]')
        if t_code.startswith("[") and t_code.endswith("]"):
            try:
                # ვასუფთავებთ ფრჩხილებისგან და ვაქცევთ ნამდვილ ლისტად
                clean_list = t_code.replace("[", "").replace("]", "").replace("'", "").replace('"', "").split(",")
                new_vins = [x.strip() for x in clean_list if x.strip()]
                
                # ახლა ვნახოთ vins სვეტში რა წერია. თუ იქ ჩვეულებრივი ტექსტია, ესეიგი ეგაა ნამდვილი type_code
                if isinstance(v_ins, str) and not v_ins.startswith("["):
                    new_type_code = v_ins.strip()
                elif isinstance(v_ins, list) and len(v_ins) == 1:
                    new_type_code = str(v_ins[0]).strip()
                else:
                    new_type_code = new_vins[0] if new_vins else ""
                
                needs_update = True
            except Exception as e:
                print(f"⚠️ ვერ გავასწორე {bike.get('model')}: {e}")

        if needs_update:
            print(f"🛠️ ვასწორებ: {bike['model']} | Type Code გახდა: {new_type_code} | VINs გახდა: {new_vins}")
            supabase.table("motorcycles").update({
                "type_code": new_type_code,
                "vins": new_vins
            }).eq("id", bike["id"]).execute()
            fixed_count += 1

    if fixed_count > 0:
        print(f"\n✅ სულ წარმატებით გასწორდა {fixed_count} მოტოციკლი!")
    else:
        print("\n✅ არეული სვეტები არ მოიძებნა. ყველაფერი თავის ადგილზეა!")

except Exception as e:
    print(f"❌ შეცდომა მონაცემების წამოღებისას: {e}")