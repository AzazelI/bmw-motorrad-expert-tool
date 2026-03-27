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
# MOTORCYCLE DB LOAD (🔥 NEW FIX)
# =========================
DB_PATH = os.path.join(BASE_DIR, "specs_database", "motorcycle_specs_database.json")

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
# REGISTER
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

        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters")

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

# =========================
# LOGIN
# =========================
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

# =========================
# LOGOUT
# =========================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# =========================
# ADMIN PANEL
# =========================
@app.route("/admin")
@login_required
def admin():

    users = load_users()

    if users.get(current_user.id, {}).get("role") != "admin":
        return "Access Denied", 403

    return render_template("admin.html", users=users)

# =========================
# 🔍 SEARCH (🔥 FIXED)
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

        vin_code = query[3:7] if len(query) >= 7 else query

        for bike in database:

            model = str(bike.get("model", "")).upper()
            type_code = str(bike.get("type_code", "")).upper()

            vin_data = bike.get("vin", bike.get("vin_codes", []))

            if isinstance(vin_data, str):
                vin_list = [vin_data.upper()]
            elif isinstance(vin_data, list):
                vin_list = [str(v).upper() for v in vin_data]
            else:
                vin_list = []

            match = False

            if query in model:
                match = True
            elif query == type_code:
                match = True
            elif query in vin_list:
                match = True
            elif vin_code in vin_list:
                match = True

            if match:
                results.append(bike)

        if not results:
            return jsonify({"error": "Model not found"})

        return jsonify(results)

    except Exception as e:
        print("❌ SEARCH ERROR:", e)
        return jsonify({"error": "Server error"})

# =========================
# JWT
# =========================
@app.route("/api/login", methods=["POST"])
@limiter.limit("10 per minute")
def api_login():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data"}), 400

    username = data.get("username")
    password = data.get("password")

    users = load_users()

    if username in users:
        if bcrypt.check_password_hash(users[username]["password"], password):
            token = create_access_token(identity=username)
            return jsonify(access_token=token)

    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/protected", methods=["GET"])
@jwt_required()
def protected():
    user = get_jwt_identity()
    return jsonify(logged_in_as=user)

# =========================
# MAIN
# =========================
@app.route("/")
@login_required
def home():
    return render_template("index.html", user=current_user.id)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    print("🚀 SERVER STARTED")
    app.run(host="127.0.0.1", port=5000, debug=True)