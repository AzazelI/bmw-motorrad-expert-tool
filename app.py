from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from supabase import create_client, Client
from datetime import datetime

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# უსაფრთხოების გასაღებები
app.config['SECRET_KEY'] = 'super_secret_key_123'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key_456'

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# =========================
# ☁️ SUPABASE SETUP
# =========================
SUPABASE_URL = "https://xxtwhxvafgkdrtuqqetu.supabase.co"
SUPABASE_KEY = "sb_publishable_js3pEbUOHt__E9EBIoSYfQ_5qVCBImI" 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# 🔥 RATE LIMITER
# =========================
limiter = Limiter(get_remote_address)
limiter.init_app(app)

# =========================
# LOGIN SETUP
# =========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# =========================
# USER CLASS & LOADER
# =========================
class User(UserMixin):
    def __init__(self, username, role):
        self.id = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    try:
        response = supabase.table("users").select("username, role").eq("username", user_id).execute()
        user_data = response.data
        if user_data:
            return User(user_data[0]["username"], user_data[0]["role"])
    except Exception as e:
        print(f"❌ Supabase Load User Error: {e}")
    return None

# =========================
# 📊 LOGGING LOGIC
# =========================
def log_search(username, query):
    """ ინახავს ძებნის ისტორიას Supabase-ში """
    try:
        supabase.table("search_logs").insert({
            "username": username,
            "query": query
        }).execute()
    except Exception as e:
        print(f"⚠️ Logging Error: {e}")

# =========================
# ROUTES (REGISTER & LOGIN)
# =========================
@app.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return render_template("register.html", error="შეავსეთ ყველა ველი")
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        try:
            check_user = supabase.table("users").select("username").eq("username", username).execute()
            if check_user.data:
                return render_template("register.html", error="მომხმარებელი უკვე არსებობს")
            supabase.table("users").insert({
                "username": username, 
                "password": hashed_pw, 
                "role": "user"
            }).execute()
            return redirect(url_for("login"))
        except Exception as e:
            print(f"❌ Register Error: {e}")
            return render_template("register.html", error="სერვერის შეცდომა")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
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
        except Exception as e:
            print(f"❌ Login Error: {e}")
    return render_template("login.html", error="არასწორი მონაცემები")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# =========================
# 🔍 SEARCH LOGIC (POWERED BY SUPABASE)
# =========================
@app.route("/search", methods=["POST"])
@login_required
def search():
    try:
        data = request.get_json()
        query = str(data.get("query", "")).strip().upper()
        if not query:
            return jsonify({"error": "Empty query"})
        
        log_search(current_user.id, query)
        
        # 🚀 1. ვიღებთ მონაცემებს პირდაპირ Supabase-დან
        db_response = supabase.table("motorcycles").select("*").execute()
        motor_database = db_response.data
        
        results = []
        vin_code = query[3:7] if len(query) >= 7 else query

        # 🚀 2. ვძებნით Supabase-დან წამოღებულ მონაცემებში
        for bike in motor_database:
            model = str(bike.get("model", "")).upper()
            type_code = str(bike.get("type_code", "")).upper()
            engine_type = str(bike.get("engine_type", "")).upper()
            
            vin_data = bike.get("vins", [])
            if isinstance(vin_data, str): 
                vin_list = [vin_data.upper()]
            elif isinstance(vin_data, list): 
                vin_list = [str(v).upper() for v in vin_data]
            else: 
                vin_list = []

            match = False
            detected = "—"
            
            if query in model or query == type_code or query in engine_type:
                match = True
                detected = vin_list[0] if vin_list else "—"
            elif query in vin_list or vin_code in vin_list:
                match = True
                detected = query if len(query) >= 7 else (vin_list[0] if vin_list else "—")

            if match:
                bike_copy = bike.copy()
                bike_copy["detected_vin"] = detected
                results.append(bike_copy)

        if not results: 
            return jsonify({"error": "Model not found"})
        return jsonify(results)
        
    except Exception as e:
        print("❌ SEARCH ERROR:", e)
        return jsonify({"error": "Server error"})

# =========================
# ADMIN PANEL FUNCTIONS
# =========================
@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        return "Access Denied", 403
    try:
        response = supabase.table("users").select("username, role").execute()
        users_list = response.data
        users_dict = {u["username"]: {"role": u["role"]} for u in users_list}
        logs = []
        try:
            log_res = supabase.table("search_logs").select("*").order("created_at", desc=True).limit(20).execute()
            logs = log_res.data
        except: pass
        return render_template("admin.html", users=users_dict, logs=logs)
    except Exception as e:
        print(f"❌ Admin Page Error: {e}")
        return "Database Error", 500

@app.route("/clear-logs", methods=["POST"])
@login_required
def clear_logs():
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    try:
        supabase.table("search_logs").delete().neq("id", 0).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
    except Exception as e:
        return "Error adding user", 500

@app.route("/delete-user/<username>", methods=["POST"])
@login_required
def delete_user(username):
    if current_user.role != "admin" or username == current_user.id: return redirect(url_for("admin"))
    try:
        supabase.table("users").delete().eq("username", username).execute()
        return redirect(url_for("admin"))
    except: return "Error deleting user", 500

@app.route("/")
@login_required
def home():
    return render_template("index.html", user=current_user.id, role=current_user.role)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))