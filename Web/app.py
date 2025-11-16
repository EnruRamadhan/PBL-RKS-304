from datetime import datetime
import pytz
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import bcrypt

# ----- Inisialisasi Flask -----
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get("SECRET_KEY", "secret-key-default")
app.config['PERMANENT_SESSION_LIFETIME'] = 3600000  # 1 hour

# ----- Konfigurasi koneksi ke database -----
db_config = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASS", "root123"),
    "database": os.environ.get("DB_NAME", "wisata_db"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "auth_plugin": "mysql_native_password"
}

def get_db():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def test_connection():
    """Test koneksi database"""
    try:
        conn = mysql.connector.connect(**db_config)
        print("✅ Database connection successful!")
        
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✅ Tables in database: {tables}")
        
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
        return False

def init_database():
    """Initialize database and create tables if not exists"""
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        try:
            # create pelanggan schema that matches existing schema (safe: IF NOT EXISTS)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pelanggan (
                    id_pelanggan INT AUTO_INCREMENT PRIMARY KEY,
                    nama VARCHAR(100) NOT NULL,
                    username VARCHAR(100) UNIQUE,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    no_hp VARCHAR(20),
                    tanggal_daftar DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("✅ Table pelanggan initialized successfully (if not exists)")
        except mysql.connector.Error as err:
            print(f"❌ Error initializing database: {err}")
        finally:
            cursor.close()
            conn.close()

# ------------------------------
# ROUTES FRONTEND
# ------------------------------

# Landing page
@app.route('/')
@app.route('/landing')
def landing():
    # Clear session jika ada
    session.clear()
    return render_template('landing.html')

# Home page setelah login
@app.route('/home')
def home():
    if 'pelanggan_id' not in session or not session.get('logged_in'):
        print("❌ User not logged in, redirecting to login")
        return redirect(url_for('login'))
    
    print(f"✅ User {session['pelanggan_username']} accessing home")
    return render_template('index.html', username=session.get('pelanggan_username'))

# Index page (alias untuk home) - GUNAKAN ENDPOINT NAME YANG BERBEDA
@app.route('/index')
def index_page():  # GANTI NAMA FUNCTION INI
    if 'pelanggan_id' not in session or not session.get('logged_in'):
        print("❌ User not logged in, redirecting to login")
        return redirect(url_for('login'))
    
    print(f"✅ User {session['pelanggan_username']} accessing index")
    return render_template('index.html', username=session.get('pelanggan_username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        print(f"🔍 Login attempt: {username}")

        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True, buffered=True)

            try:
                # 🔎 1. Cek dulu apakah dia ADMIN
                cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
                admin = cursor.fetchone()

                if admin:
                    print("🔍 Admin found:", admin["username"])

                    if bcrypt.checkpw(password.encode("utf-8"), admin["password"].encode("utf-8")):
                        # 🎉 Login admin OK
                        session.clear()
                        session["admin_id"] = admin["id_admin"]
                        session["admin_username"] = admin["username"]
                        session["admin_role"] = admin["role"]
                        session["logged_in_admin"] = True

                        print("✅ ADMIN LOGIN SUCCESS:", admin["username"])
                        return redirect(url_for("admin_index"))  # buat halaman admin nanti
                    else:
                        error = "Password admin salah!"
                        return render_template("login.html", error=error)

                # 🔎 2. Jika bukan admin → cek sebagai pelanggan
                cursor.execute(
                    "SELECT id_pelanggan, username, password FROM pelanggan WHERE username=%s",
                    (username,)
                )
                user = cursor.fetchone()

                if user:
                    print("🔍 Pelanggan found:", user["username"])

                    if bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
                        session.clear()
                        session["pelanggan_id"] = user["id_pelanggan"]
                        session["pelanggan_username"] = user["username"]
                        session["logged_in"] = True

                        print("✅ Pelanggan login success:", user["username"])
                        return redirect(url_for("home"))

                    else:
                        error = "Password salah!"
                else:
                    error = "Username tidak ditemukan."

            except mysql.connector.Error as err:
                print("❌ Database error:", err)
                error = f"Database error: {err}"

            finally:
                cursor.close()
                conn.close()

    return render_template("login.html", error=error)

# Register Pelanggan
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        print(f"🔍 Registration attempt - Username: {username}")

        if not all([username, email, password, confirm_password]):
            error = "Semua field wajib diisi!"
        elif password != confirm_password:
            error = "Password tidak cocok!"
        elif len(password) < 6:
            error = "Password minimal 6 karakter!"
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            conn = get_db()
            if conn:
                try:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO pelanggan (nama, username, email, password) VALUES (%s, %s, %s, %s)",
                            (username, username, email, hashed_password)
                        )
                        conn.commit()
                        print(f"✅ Registration successful - Username: {username}")
                        return redirect(url_for('login'))
                except mysql.connector.Error as err:
                    if err.errno == 1062:  # Duplicate entry
                        error = "Username atau email sudah terdaftar!"
                    else:
                        error = f"Gagal menyimpan data: {err}"
                finally:
                    conn.close()
            else:
                error = "Tidak dapat terhubung ke database"

    return render_template('register.html', error=error)

@app.route("/checkout", methods=["POST"])
def checkout():
    if "pelanggan_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    print("📌 DATA MASUK CHECKOUT:", data)

    # Ambil data dari front-end
    nama_tiket = data.get("nama_tiket")
    jumlah = data.get("jumlah")
    harga = data.get("harga")
    tanggal_kunjungan = data.get("tanggal")  # masih dalam bentuk string
    user_id = session["pelanggan_id"]

    # Buat format datetime WIB (object, bukan string)
    tz = pytz.timezone("Asia/Jakarta")
    tanggal_pembelian = datetime.now(tz)

    # Konversi tanggal kunjungan (string → date)
    try:
        tanggal_kunjungan = datetime.strptime(tanggal_kunjungan, "%Y-%m-%d").date()
    except:
        return jsonify({"error": "Format tanggal kunjungan tidak valid"}), 400

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO tiket (user_id, nama_tiket, tanggal_kunjungan, tanggal_pembelian, jumlah, harga)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            nama_tiket,
            tanggal_kunjungan,
            tanggal_pembelian,
            jumlah,
            harga
        ))

        conn.commit()
        print("✅ Tiket berhasil disimpan!")
        return jsonify({"status": "success", "message": "Tiket berhasil disimpan"})

    except Exception as e:
        print("❌ ERROR simpan tiket:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route("/tiket")
def tiket_saya():
    # Cek apakah user sudah login
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session.get("pelanggan_id")

    conn = get_db()
    tickets = []

    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id_tiket, nama_tiket, tanggal_kunjungan, tanggal_pembelian, jumlah, harga, total
                FROM tiket
                WHERE user_id = %s
                ORDER BY tanggal_pembelian DESC
            """, (user_id,))
            tickets = cursor.fetchall()

        except mysql.connector.Error as err:
            print("❌ Error mengambil tiket:", err)

        finally:
            cursor.close()
            conn.close()

    return render_template("tiket.html", tickets=tickets)

# Kontak
@app.route('/kontak')
def kontak():
    return render_template('kontak.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

@app.route('/admin/index')
def admin_index():
    if not session.get("logged_in_admin"):
        return redirect(url_for("login"))

    return render_template("index.html", username=session.get("admin_username"))

# ------------------------------
# Jalankan aplikasi
# ------------------------------
if __name__ == '__main__':
    print("🚀 Starting Flask application...")
    print("Testing database connection...")
    
    if test_connection():
        print("Initializing database...")
        init_database()
        print("📱 Alternative: http://127.0.0.1:5000")
        print("⚡ Debug mode: ON")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ Cannot start application due to database connection issue")