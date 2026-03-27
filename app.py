from flask import Flask, render_template, request, jsonify, redirect, url_for
import json, os

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

app.config['SECRET_KEY'] = 'super_secret_key_123'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key_456'

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

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
# USERS DB
# =========================
BASE_DIR = os.path.dirname(__file__)
USERS_DB_PATH = os.path.join(BASE_DIR, "users.json")

if not os.path.exists(USERS_DB_PATH):
    with open(USERS_DB_PATH, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USERS_DB_PATH, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

# =========================
# MOTORCYCLE DB LOAD
# =========================
DB_PATH = os.path.join(BASE_DIR, "specs_database", "motorcycle_specs_database.json")

if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(BASE_DIR, "motorcycle_specs_database.json")

try:
    with open(DB_PATH, "r", encoding="utf-8") as f:
        database = json.load(f)
        print(f"✅ DB Loaded: {len(database)} bikes")
except Exception as e:
    print("❌ DB ERROR:", e)
    database = []

# =========================
# USER CLASS
# =========================
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    if user_id in users:
        return User(user_id)
    return None

# =========================
# REGISTER & LOGIN ROUTES
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
            return render_template("register.html", error="Fill all fields")
        users = load_users()
        if username in users:
            return render_template("register.html", error="User already exists")
        users[username] = {
            "password": bcrypt.generate_password_hash(password).decode("utf-8"),
            "role": "user"
        }
        save_users(users)
        return redirect(url_for("login"))
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
        users = load_users()
        if username in users:
            if bcrypt.check_password_hash(users[username]["password"], password):
                login_user(User(username), remember=remember)
                return redirect(url_for("home"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# =========================
# 🔍 SEARCH (FIXED WITH VIN DETECTION)
# =========================
@app.route("/search", methods=["POST"])
@login_required
def search():
    try:
        data = request.get_json()
        query = str(data.get("query", "")).strip().upper()

        if not query:
            return jsonify({"error": "Empty query"})

        results = []
        # VIN-ის 4 სიმბოლო (მე-4-დან მე-7-მდე)
        extracted_vin = query[3:7] if len(query) >= 7 else query

        for bike in database:
            model = str(bike.get("model", "")).upper()
            type_code = str(bike.get("type_code", "")).upper()
            
            # VIN კოდების დამუშავება
            v_val = bike.get("vin", bike.get("vin_codes", []))
            if isinstance(v_val, str):
                vin_list = [v_val.upper()]
            elif isinstance(v_val, list):
                vin_list = [str(v).upper() for v in v_val]
            else:
                vin_list = []

            match = False
            detected = "—"

            # 1. ძებნა მოდელით ან ტიპის კოდით
            if query in model or query == type_code:
                match = True
                detected = vin_list[0] if vin_list else "—"
            
            # 2. ძებნა VIN-ით (სრული ან ამოჭრილი)
            elif query in vin_list:
                match = True
                detected = query
            elif extracted_vin in vin_list:
                match = True
                detected = extracted_vin

            if match:
                # ვქმნით ასლს და ვამატებთdetected_vin ველს
                bike_data = bike.copy()
                bike_data["detected_vin"] = detected
                results.append(bike_data)

        if not results:
            return jsonify({"error": "Model not found"})

        return jsonify(results)

    except Exception as e:
        print("❌ SEARCH ERROR:", e)
        return jsonify({"error": "Server error"})

# =========================
# ADMIN PANEL & HOME
# =========================
@app.route("/admin")
@login_required
def admin():
    users = load_users()
    if users.get(current_user.id, {}).get("role") != "admin":
        return "Access Denied", 403
    return render_template("admin.html", users=users)

@app.route("/")
@login_required
def home():
    return render_template("index.html", user=current_user.id)

# =========================
# API / JWT
# =========================
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    if not data: return jsonify({"error": "No data"}), 400
    username, password = data.get("username"), data.get("password")
    users = load_users()
    if username in users and bcrypt.check_password_hash(users[username]["password"], password):
        token = create_access_token(identity=username)
        return jsonify(access_token=token)
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)