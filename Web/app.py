import os
from flask import Flask, render_template, request, redirect, url_for, session
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
    if 'user_id' not in session or not session.get('logged_in'):
        print("❌ User not logged in, redirecting to login")
        return redirect(url_for('login'))
    
    print(f"✅ User {session['user_name']} accessing home")
    return render_template('index.html', username=session.get('user_name'))

# Index page (alias untuk home) - GUNAKAN ENDPOINT NAME YANG BERBEDA
@app.route('/index')
def index_page():  # GANTI NAMA FUNCTION INI
    if 'user_id' not in session or not session.get('logged_in'):
        print("❌ User not logged in, redirecting to login")
        return redirect(url_for('login'))
    
    print(f"✅ User {session['user_name']} accessing index")
    return render_template('index.html', username=session.get('user_name'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"🔍 Login attempt - Username: {username}")

        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                # gunakan nama kolom yang ada: id_pelanggan sebagai id
                cursor.execute("SELECT id_pelanggan AS id, username, password FROM pelanggan WHERE username = %s", (username,))
                user = cursor.fetchone()
                
                if user:
                    print(f"🔍 User found: {user['username']}")
                    if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                        session['user_id'] = user['id']
                        session['user_name'] = user['username']
                        session['logged_in'] = True
                        
                        print(f"✅ Login successful - User: {user['username']}")
                        return redirect(url_for('home'))
                    else:
                        error = "Password salah."
                else:
                    error = "Username tidak ditemukan."
            except mysql.connector.Error as err:
                error = f"Database error: {err}"
                print(f"❌ Database error: {err}")
            finally:
                cursor.close()
                conn.close()
        else:
            error = "Tidak dapat terhubung ke database"

    return render_template('login.html', error=error)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
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
                cursor = conn.cursor()
                try:
                    # pelanggan.nama wajib -> pakai username sebagai nama default
                    cursor.execute(
                        "INSERT INTO pelanggan (nama, username, email, password) VALUES (%s, %s, %s, %s)",
                        (username, username, email, hashed_password)
                    )
                    conn.commit()
                    return redirect(url_for('login'))
                except mysql.connector.Error as err:
                    if err.errno == 1062:  # Duplicate entry
                        error = "Username atau email sudah terdaftar!"
                    else:
                        error = f"Gagal menyimpan data: {err}"
                finally:
                    cursor.close()
                    conn.close()
            else:
                error = "Tidak dapat terhubung ke database"

    return render_template('register.html', error=error)

# Kontak
@app.route('/kontak')
def kontak():
    return render_template('kontak.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

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