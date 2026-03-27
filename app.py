from flask import Flask, render_template, request, jsonify, redirect, url_for
import json, os, sqlite3

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
# 🔥 RATE LIMITER (უსაფრთხოებისთვის)
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
# 🗄️ SQLITE DATABASE SETUP
# =========================
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # იუზერების ცხრილის შექმნა (თუ არ არსებობს)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# =========================
# MOTORCYCLE JSON LOAD (მხოლოდ კითხვის რეჟიმი)
# =========================
MOTOR_DB_PATH = os.path.join(BASE_DIR, "specs_database", "motorcycle_specs_database.json")
if not os.path.exists(MOTOR_DB_PATH):
    MOTOR_DB_PATH = os.path.join(BASE_DIR, "motorcycle_specs_database.json")

try:
    with open(MOTOR_DB_PATH, "r", encoding="utf-8") as f:
        motor_database = json.load(f)
        print(f"✅ Motor DB Loaded: {len(motor_database)} bikes")
except Exception as e:
    print("❌ Motor DB ERROR:", e)
    motor_database = []

# =========================
# USER CLASS & LOADER
# =========================
class User(UserMixin):
    def __init__(self, username, role):
        self.id = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users WHERE username = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(user_data[0], user_data[1])
    return None

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
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                           (username, hashed_pw, "user"))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="მომხმარებელი უკვე არსებობს")

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

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT username, password, role FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row and bcrypt.check_password_hash(row[1], password):
            login_user(User(row[0], row[2]), remember=remember)
            return redirect(url_for("home"))

        return render_template("login.html", error="არასწორი მონაცემები")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# =========================
# 🔍 SEARCH LOGIC
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

        for bike in motor_database:
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
            detected = "—"

            if query in model or query == type_code:
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
# ADMIN PANEL
# =========================
@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        return "Access Denied", 403

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users")
    rows = cursor.fetchall()
    conn.close()
    
    users_dict = {row[0]: {"role": row[1]} for row in rows}
    return render_template("admin.html", users=users_dict)

@app.route("/")
@login_required
def home():
    return render_template("index.html", user=current_user.id)

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
