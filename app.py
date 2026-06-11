from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# =========================
# 🔒 უსაფრთხოების გასაღებები
# =========================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super_secret_key_123')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt_secret_key_456')

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# =========================
# ☁️ SUPABASE SETUP
# =========================
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://xxtwhxvafgkdrtuqqetu.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'sb_publishable_js3pEbUOHt__E9EBIoSYfQ_5qVCBImI') 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# ⚡ IN-MEMORY CACHE FOR MOTORCYCLES DATABASE
# ==========================================
_motorcycles_cache = None

def get_motorcycles():
    global _motorcycles_cache
    if _motorcycles_cache is None:
        print("🔄 Loading motorcycles from Supabase into memory cache...")
        try:
            response = supabase.table("motorcycles").select("*").execute()
            _motorcycles_cache = response.data
            print(f"✅ Loaded {len(_motorcycles_cache)} motorcycles into cache.")
        except Exception as e:
            print(f"❌ Error loading motorcycles from Supabase: {e}")
            _motorcycles_cache = []
    return _motorcycles_cache

def clear_motorcycles_cache():
    global _motorcycles_cache
    _motorcycles_cache = None
    print("🧹 Motorcycles memory cache cleared.")

# =========================
# 🔥 RATE LIMITER & LOGIN
# =========================
limiter = Limiter(get_remote_address)
limiter.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, username, role):
        self.id = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    try:
        response = supabase.table("users").select("username, role").eq("username", user_id).execute()
        user_data = response.data
        if user_data: return User(user_data[0]["username"], user_data[0]["role"])
    except: pass
    return None

def log_search(username, query):
    try: supabase.table("search_logs").insert({"username": username, "query": query}).execute()
    except: pass


# =========================
# 🔑 AUTH ROUTES
# =========================
@app.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated: return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password: return render_template("register.html", error="შეავსეთ ყველა ველი")
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        try:
            check_user = supabase.table("users").select("username").eq("username", username).execute()
            if check_user.data: return render_template("register.html", error="მომხმარებელი უკვე არსებობს")
            supabase.table("users").insert({"username": username, "password": hashed_pw, "role": "user"}).execute()
            return redirect(url_for("login"))
        except: return render_template("register.html", error="სერვერის შეცდომა")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated: return redirect(url_for("home"))
    
    error = None # ვამატებთ error ცვლადს, რომელიც GET მოთხოვნისას ცარიელია
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False
        try:
            response = supabase.table("users").select("*").eq("username", username).execute()
            user_data = response.data
            if user_data and bcrypt.check_password_hash(user_data[0]["password"], password):
                user_obj = User(user_data[0]["username"], user_data[0]["role"])
                login_user(user_obj, remember=remember)
                return redirect(url_for("home"))
            else:
                error = "არასწორი მონაცემები" # ერორი ენიჭება მხოლოდ არასწორი მონაცემების დროს
        except: 
            error = "არასწორი მონაცემები"
            
    # GET-ზე გადააწვდის error=None, ხოლო POST-ზე შეცდომის ტექსტს
    return render_template("login.html", error=error)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# =========================
# 🔍 SEARCH
# =========================
@app.route("/search", methods=["POST"])
@login_required
def search():
    try:
        data = request.get_json()
        query = str(data.get("query", "")).strip().upper()
        if not query: return jsonify({"error": "Empty query"})
        
        log_search(current_user.id, query)
        motor_database = get_motorcycles()
        results = []
        
        # ვშლით სფეისებს საძიებო სიტყვიდან (მაგ: "K 1600" ხდება "K1600")
        clean_query = query.replace(" ", "")
        vin_code = query[3:7] if len(query) >= 7 else query

        for bike in motor_database:
            model = str(bike.get("model", "")).upper()
            type_code = str(bike.get("type_code", "")).upper()
            engine_type = str(bike.get("engine_type", "")).upper()
            
            # ვშლით სფეისებს ბაზაში არსებული ჩანაწერებიდანაც
            clean_model = model.replace(" ", "")
            clean_type_code = type_code.replace(" ", "")
            clean_engine_type = engine_type.replace(" ", "")
            
            vin_data = bike.get("vins", [])
            vin_list = [str(v).upper() for v in vin_data] if isinstance(vin_data, list) else ([str(vin_data).upper()] if isinstance(vin_data, str) else [])

            match = False
            detected = "—"
            
            # ვადარებთ გასუფთავებულ ვერსიებს ერთმანეთს
            if (clean_query in clean_model) or (clean_query in clean_type_code) or (clean_query in clean_engine_type):
                match = True
                detected = vin_list[0] if vin_list else "—"
            elif query in vin_list or vin_code in vin_list:
                match = True
                detected = query if len(query) >= 7 else (vin_list[0] if vin_list else "—")

            if match:
                bike_copy = bike.copy()
                bike_copy["detected_vin"] = detected
                results.append(bike_copy)

        if not results: return jsonify({"error": "Model not found"})
        return jsonify(results)
    except Exception as e:
        print("Search error:", e)
        return jsonify({"error": "Server error"})

# =========================
# 🛠️ ADMIN PANEL
# =========================
@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin": return "Access Denied", 403
    try:
        users_res = supabase.table("users").select("username, role").execute()
        users_dict = {u["username"]: {"role": u["role"]} for u in users_res.data}
        
        num_admins = sum(1 for u in users_res.data if u.get("role") == "admin")
        num_users = sum(1 for u in users_res.data if u.get("role") == "user")
        
        total_searches = 0
        popular_queries = []
        try:
            count_res = supabase.table("search_logs").select("id", count="exact").execute()
            total_searches = count_res.count if count_res.count is not None else 0
            
            all_queries_res = supabase.table("search_logs").select("query").execute()
            queries = [log["query"] for log in all_queries_res.data if log.get("query")]
            from collections import Counter
            popular_queries = Counter(queries).most_common(5)
        except Exception as e:
            print("Error computing search statistics:", e)

        logs = []
        try:
            log_res = supabase.table("search_logs").select("*").order("created_at", desc=True).limit(20).execute()
            logs = log_res.data
        except: pass

        bikes = []
        try:
            bike_res = supabase.table("motorcycles").select("*").order("id", desc=True).execute()
            bikes = bike_res.data
        except: pass

        return render_template(
            "admin.html", 
            users=users_dict, 
            logs=logs, 
            bikes=bikes,
            total_bikes=len(get_motorcycles()),
            num_admins=num_admins,
            num_users=num_users,
            total_searches=total_searches,
            popular_queries=popular_queries
        )
    except Exception as e:
        print("Admin dashboard error:", e)
        return "Database Error", 500


# --- მოტოციკლის დამატება ---
@app.route("/add-bike", methods=["POST"])
@login_required
def add_bike():
    if current_user.role != "admin": return "Unauthorized", 403
    try:
        vins_raw = request.form.get("vins", "")
        sources_raw = request.form.get("sources", "")
        
        new_bike = {
            "model": request.form.get("model", ""),
            "type_code": request.form.get("type_code", ""),
            "engine_cc": request.form.get("engine_cc", ""),
            "power_kw": request.form.get("power_kw", ""),
            "horsepower": request.form.get("horsepower", ""),
            "kerb_weight_kg": request.form.get("kerb_weight_kg", ""),
            "gross_weight_kg": request.form.get("gross_weight_kg", ""),
            "payload_kg": request.form.get("payload_kg", ""),
            "engine_type": request.form.get("engine_type", ""),
            "fuel": request.form.get("fuel", ""),
            "vins": [v.strip() for v in vins_raw.split(",") if v.strip()],
            "sources": [s.strip() for s in sources_raw.split(",") if s.strip()]
        }
        supabase.table("motorcycles").insert(new_bike).execute()
        clear_motorcycles_cache()
        return redirect(url_for("admin"))
    except: return "Error adding motorcycle", 500

# --- 🚀 მოტოციკლის რედაქტირება (ახალი) ---
@app.route("/edit-bike/<int:bike_id>", methods=["POST"])
@login_required
def edit_bike(bike_id):
    if current_user.role != "admin": return "Unauthorized", 403
    try:
        vins_raw = request.form.get("vins", "")
        sources_raw = request.form.get("sources", "")
        
        updated_bike = {
            "model": request.form.get("model", ""),
            "type_code": request.form.get("type_code", ""),
            "engine_cc": request.form.get("engine_cc", ""),
            "power_kw": request.form.get("power_kw", ""),
            "horsepower": request.form.get("horsepower", ""),
            "kerb_weight_kg": request.form.get("kerb_weight_kg", ""),
            "gross_weight_kg": request.form.get("gross_weight_kg", ""),
            "payload_kg": request.form.get("payload_kg", ""),
            "engine_type": request.form.get("engine_type", ""),
            "fuel": request.form.get("fuel", ""),
            "vins": [v.strip() for v in vins_raw.split(",") if v.strip()],
            "sources": [s.strip() for s in sources_raw.split(",") if s.strip()]
        }
        supabase.table("motorcycles").update(updated_bike).eq("id", bike_id).execute()
        clear_motorcycles_cache()
        return redirect(url_for("admin"))
    except Exception as e:
        print("Error:", e)
        return "Error editing motorcycle", 500

@app.route("/delete-bike/<int:bike_id>", methods=["POST"])
@login_required
def delete_bike(bike_id):
    if current_user.role != "admin": return "Unauthorized", 403
    try:
        supabase.table("motorcycles").delete().eq("id", bike_id).execute()
        clear_motorcycles_cache()
        return redirect(url_for("admin"))
    except: return "Error deleting motorcycle", 500

# --- 🚀 იუზერის რედაქტირება (ახალი) ---
@app.route("/edit-user/<username>", methods=["POST"])
@login_required
def edit_user(username):
    if current_user.role != "admin": return "Unauthorized", 403
    try:
        new_password = request.form.get("password", "").strip()
        new_role = request.form.get("role", "user")
        
        update_data = {"role": new_role}
        if new_password: # თუ ახალი პაროლი ჩაწერა, ვაახლებთ მაგასაც
            update_data["password"] = bcrypt.generate_password_hash(new_password).decode("utf-8")
            
        supabase.table("users").update(update_data).eq("username", username).execute()
        return redirect(url_for("admin"))
    except Exception as e:
        print("Error:", e)
        return "Error editing user", 500

@app.route("/add-user", methods=["POST"])
@login_required
def add_user():
    if current_user.role != "admin": return jsonify({"error": "Unauthorized"}), 403
    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role", "user")
    if not username or not password: return redirect(url_for("admin"))
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    try:
        supabase.table("users").insert({"username": username, "password": hashed_pw, "role": role}).execute()
        return redirect(url_for("admin"))
    except: return "Error adding user", 500

@app.route("/delete-user/<username>", methods=["POST"])
@login_required
def delete_user(username):
    if current_user.role != "admin" or username == current_user.id: return redirect(url_for("admin"))
    try:
        supabase.table("users").delete().eq("username", username).execute()
        return redirect(url_for("admin"))
    except: return "Error deleting user", 500

@app.route("/clear-logs", methods=["POST"])
@login_required
def clear_logs():
    if current_user.role != "admin": return jsonify({"error": "Unauthorized"}), 403
    try:
        supabase.table("search_logs").delete().neq("id", 0).execute()
        return jsonify({"status": "success"})
    except: return jsonify({"status": "error"}), 500

# =========================
# 📂 PDF DOCUMENT MANAGER
# =========================
DOCS_DIR = os.path.join(app.root_path, "static", "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

@app.route("/api/docs", methods=["GET"])
@login_required
def list_docs():
    try:
        files = []
        for filename in os.listdir(DOCS_DIR):
            if filename.lower().endswith(".pdf"):
                filepath = os.path.join(DOCS_DIR, filename)
                size_bytes = os.path.getsize(filepath)
                if size_bytes >= 1024 * 1024:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                
                files.append({
                    "name": filename,
                    "size": size_str,
                    "url": url_for("static", filename=f"docs/{filename}")
                })
        return jsonify(files)
    except Exception as e:
        print("Error listing documents:", e)
        return jsonify({"error": "Failed to list documents"}), 500

@app.route("/upload-doc", methods=["POST"])
@login_required
def upload_doc():
    if current_user.role != "admin": return "Unauthorized", 403
    try:
        if "doc" not in request.files:
            return "No file part", 400
        file = request.files["doc"]
        if file.filename == "":
            return "No selected file", 400
            
        if file:
            filename = file.filename
            if not filename.lower().endswith(".pdf"):
                return "Only PDF files are allowed", 400
            
            if file.content_type != "application/pdf":
                return "Invalid file type. Must be application/pdf", 400
                
            file.seek(0, os.SEEK_END)
            size_bytes = file.tell()
            file.seek(0)
            if size_bytes > 15 * 1024 * 1024:
                return "File is too large. Max size is 15MB", 400
                
            from werkzeug.utils import secure_filename
            safe_filename = secure_filename(filename)
            if not safe_filename:
                safe_filename = f"manual_{int(datetime.now().timestamp())}.pdf"
                
            file.save(os.path.join(DOCS_DIR, safe_filename))
            return redirect(request.referrer or url_for("home"))
    except Exception as e:
        print("Upload error:", e)
        return "Error uploading file", 500

@app.route("/")
@login_required
def home():
    return render_template("index.html", user=current_user.id, role=current_user.role)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
# Trigger redeploy to clear stuck Render queue