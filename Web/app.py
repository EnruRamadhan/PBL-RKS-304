from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import bcrypt
from functools import wraps
from math import ceil
import os
from datetime import datetime
import pytz
from flask import flash

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
                    tanggal_daftar DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME NULL
                )
            """)
            conn.commit()
            print("✅ Table pelanggan initialized successfully (if not exists)")
        except mysql.connector.Error as err:
            print(f"❌ Error initializing database: {err}")
        finally:
            cursor.close()
            conn.close()

def login_required_pelanggan(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "pelanggan_username" not in session:
            return redirect(url_for("login_pelanggan"))
        return f(*args, **kwargs)
    return decorated_function

# Landing page
@app.route('/')
@app.route('/landing')
def landing():
    # Clear session jika ada
    session.clear()
    return render_template('landing.html')

# Home page setelah login
@app.route("/home")
def home():

    destinasi_statis_raw = [
        {"nama":"Pantai Nongsa","deskripsi":"Pantai populer untuk bersantai dan menikmati matahari terbenam di Batam.","jam_buka":"24 Jam","harga":10000,"gambar":"nongsa.jpg"},
        {"nama":"Pantai Melayu","deskripsi":"Pantai luas dengan pasir putih halus dan ombak yang tenang, cocok untuk keluarga.","jam_buka":"07.00 - 18.00","harga":15000,"gambar":"melayu.jpg"},
        {"nama":"Pantai Vio-Vio","deskripsi":"Menawarkan spot foto instagramable dan tempat snorkeling yang indah.","jam_buka":"08.00 - 18.00","harga":10000,"gambar":"viovio.jpeg"},
        {"nama":"Pantai Elyora","deskripsi":"Pantai dengan pemandangan indah dan area perkemahan yang nyaman.","jam_buka":"08.00 - 18.00","harga":10000,"gambar":"elyora.jpg"},
        {"nama":"Pantai Marina","deskripsi":"Tempat wisata dengan taman dan spot foto modern di pinggir pantai.","jam_buka":"07.00 - 19.00","harga":20000,"gambar":"marina.jpeg"},
        {"nama":"Pantai Melur","deskripsi":"Pantai dengan pasir putih dan suasana alami, cocok untuk liburan santai.","jam_buka":"24 Jam","harga":5000,"gambar":"melur.jpeg"},
        {"nama":"Taman Rusa","deskripsi":"Tempat wisata edukatif dengan rusa dan area jogging yang sejuk.","jam_buka":"07.00 - 18.00","harga":5000,"gambar":"tamanrusa.jpeg"},
        {"nama":"Kampung Vietnam","deskripsi":"Situs sejarah peninggalan pengungsi Vietnam dengan suasana klasik.","jam_buka":"08.00 - 17.00","harga":20000,"gambar":"kmpgvietnam.jpeg"},
        {"nama":"Mata Kucing","deskripsi":"Kawasan wisata alam dengan kolam renang, hutan, dan taman bermain.","jam_buka":"08.00 - 17.00","harga":10000,"gambar":"matakucing.jpeg"},
        {"nama":"Ocarina Park","deskripsi":"Taman hiburan keluarga dengan wahana modern di tepi laut Batam.","jam_buka":"09.00 - 21.00","harga":25000,"gambar":"ocarina.jpeg"},
    ]

    destinasi_statis = [
        {
            "id_destinasi": f"s{i}",
            "nama": d["nama"],
            "deskripsi": d["deskripsi"],
            "jam_buka": d["jam_buka"],
            "harga": d["harga"],
            "gambar": d["gambar"]
        }
        for i, d in enumerate(destinasi_statis_raw, start=1)
    ]

    destinasi_admin = []
    conn = get_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id_destinasi, nama, deskripsi, jam_buka, harga, gambar
                FROM destinasi
                ORDER BY id_destinasi DESC
            """)
            destinasi_admin = cursor.fetchall()
        except Exception as e:
            print("❌ Error fetch destinasi admin:", e)
        finally:
            cursor.close()
            conn.close()

    destinasi = destinasi_statis + destinasi_admin

    return render_template(
        "index.html",
        username=session.get("pelanggan_username", "Guest"),
        destinasi=destinasi,
        destinasi_list=destinasi   
    )

@app.route("/index")
@login_required_pelanggan
def index_page():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM destinasi ORDER BY is_statis DESC, id_destinasi ASC")
    destinasi = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        username=session.get("pelanggan_username"),
        destinasi=destinasi
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        if conn is None:
            error = "Tidak dapat terhubung ke database"
            return render_template("login.html", error=error)

        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            # cek admin
            cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
            admin = cursor.fetchone()
            if admin:
                if bcrypt.checkpw(password.encode("utf-8"), admin["password"].encode("utf-8")):
                    session.clear()
                    session["admin_id"] = admin["id_admin"]
                    session["admin_username"] = admin["username"]
                    session["admin_role"] = admin.get("role")
                    session["logged_in_admin"] = True
                    flash("Admin login berhasil.", "success")
                    return redirect(url_for("admin_dashboard"))
                else:
                    error = "Password admin salah!"
                    return render_template("login.html", error=error)

            # cek pelanggan
            cursor.execute("SELECT id_pelanggan, username, password FROM pelanggan WHERE username=%s", (username,))
            user = cursor.fetchone()
            if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
                session.clear()
                session["pelanggan_id"] = user["id_pelanggan"]
                session["pelanggan_username"] = user["username"]
                session["logged_in"] = True
                flash("Login berhasil.", "success")
                return redirect(url_for("home"))
            else:
                if not user:
                    error = "Username tidak ditemukan."
                else:
                    error = "Password salah!"
        except mysql.connector.Error as err:
            print("❌ Database error:", err)
            error = "Database error."
        finally:
            cursor.close()
            conn.close()

    return render_template("login.html", error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', "").strip()
        email = request.form.get('email', "").strip()
        password = request.form.get('password', "")
        confirm_password = request.form.get('confirm_password', "")

        print(f"🔍 Registration attempt - Username: {username}")

        # Validasi
        if not all([username, email, password, confirm_password]):
            error = "Semua field wajib diisi!"
        elif password != confirm_password:
            error = "Password tidak cocok!"
        elif len(password) < 6:
            error = "Password minimal 6 karakter!"
        else:
            # Karena tidak ada nama, pakai username sebagai nama default
            nama = username  

            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            conn = get_db()
            if conn is None:
                error = "Tidak dapat terhubung ke database"
                return render_template('register.html', error=error)

            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO pelanggan (nama, username, email, password)
                    VALUES (%s, %s, %s, %s)
                """, (nama, username, email, hashed))

                conn.commit()
                flash("Registrasi berhasil. Silakan login.", "success")
                return redirect(url_for('login'))

            except mysql.connector.Error as err:
                print("❌ Error saat insert:", err)

                if err.errno == 1062:
                    error = "Username atau email sudah terdaftar!"
                else:
                    error = f"Gagal menyimpan data: {err}"

            finally:
                cursor.close()
                conn.close()

    return render_template('register.html', error=error)

@app.route("/pelanggan")
def pelanggan_home():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM destinasi ORDER BY nama ASC")
    destinasi_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("pelanggan.html", destinasi_list=destinasi_list)

@app.route("/checkout", methods=["POST"])
def checkout():
    if "pelanggan_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    print("📌 DATA MASUK CHECKOUT:", data)

    nama_tiket = data.get("nama_tiket")  
    jumlah = int(data.get("jumlah"))
    tanggal_kunjungan = data.get("tanggal")
    user_id = session["pelanggan_id"]

    tz = pytz.timezone("Asia/Jakarta")
    tanggal_pembelian = datetime.now(tz)

    # Validasi format tanggal
    try:
        tanggal_kunjungan = datetime.strptime(tanggal_kunjungan, "%Y-%m-%d").date()
    except:
        return jsonify({"error": "Format tanggal kunjungan tidak valid!"}), 400

    if tanggal_kunjungan < datetime.now(tz).date():
        return jsonify({"error": "Tanggal kunjungan sudah lewat!"}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        # 🔥 CARI DESTINASI BERDASARKAN NAMA (BUKAN ID)
        cursor.execute("SELECT nama, harga FROM destinasi WHERE nama = %s", (nama_tiket,))
        destinasi = cursor.fetchone()

        print("🎯 HASIL QUERY DESTINASI:", destinasi)

        if not destinasi:
            return jsonify({"error": "Destinasi tidak ditemukan"}), 400

        harga = destinasi["harga"]
        total = harga * jumlah

        # 🔥 SIMPAN PEMESANAN
        cursor.execute("""
            INSERT INTO tiket (user_id, nama_tiket, tanggal_kunjungan, tanggal_pembelian, jumlah, harga)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, nama_tiket, tanggal_kunjungan, tanggal_pembelian, jumlah, harga))

        conn.commit()

        return jsonify({
            "status": "success",
            "nama_tiket": nama_tiket,
            "jumlah": jumlah,
            "harga": harga,
            "total": total
        }), 200

    except Exception as e:
        print("❌ ERROR simpan tiket:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route("/tiket")
def tiket_saya():
    if not session.get("logged_in") and not session.get("logged_in_admin"):
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

def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in_admin"):
            return redirect(url_for("admin_login_page"))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin_login', methods=['GET'])
def admin_login_page():
    return render_template("admin_login.html")

@app.route("/admin_login", methods=["POST"])
def admin_login_post():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()

    if admin and bcrypt.checkpw(password.encode("utf-8"), admin['password'].encode("utf-8")):
        session.clear()
        session['logged_in_admin'] = True
        session['admin_username'] = admin['username']
        session['admin_id'] = admin['id_admin']
        flash("Login admin berhasil!", "success")
        return redirect(url_for("admin_dashboard"))

    flash("Username atau password salah!", "danger")
    return redirect(url_for("admin_login_page"))

@app.route("/admin")
@login_required_admin
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM tiket")
        total_tiket = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM pelanggan")
        total_users = cursor.fetchone()["total"]

        cursor.execute("SELECT SUM(total) AS total_pendapatan FROM tiket")
        total_pendapatan = cursor.fetchone()["total_pendapatan"] or 0
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "admin.html",
        section="dashboard",
        username=session.get("admin_username"),
        total_tiket=total_tiket,
        total_users=total_users,
        total_pendapatan=total_pendapatan
    )
@app.route("/admin/tiket")
@login_required_admin
def admin_tiket_page():
    page = int(request.args.get("page", 1))
    per_page = 20
    offset = (page-1)*per_page

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM tiket")
        total_items = cursor.fetchone()["total"]
        total_pages = ceil(total_items / per_page)

        cursor.execute(
            "SELECT * FROM tiket ORDER BY tanggal_pembelian DESC LIMIT %s OFFSET %s",
            (per_page, offset)
        )
        tiket = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "admin.html",
        section="tiket",
        username=session.get("admin_username"),
        tiket=tiket,
        page=page,
        total_pages=total_pages
    )

@app.route("/admin/tiket/delete/<int:id_tiket>")
@login_required_admin
def admin_delete_tiket(id_tiket):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tiket WHERE id_tiket=%s", (id_tiket,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    flash("Tiket berhasil dihapus.", "success")
    return redirect(url_for("admin_tiket_page"))

@app.route("/admin/tiket/edit/<int:id_tiket>", methods=["GET", "POST"])
@login_required_admin
def admin_edit_tiket(id_tiket):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        nama_tiket = request.form["nama_tiket"]
        jumlah = int(request.form["jumlah"])
        harga = float(request.form["harga"])
        tanggal_kunjungan = request.form["tanggal_kunjungan"]
        total = jumlah * harga
        try:
            cursor.execute("""
                UPDATE tiket SET nama_tiket=%s, jumlah=%s, harga=%s, total=%s, tanggal_kunjungan=%s
                WHERE id_tiket=%s
            """, (nama_tiket, jumlah, harga, total, tanggal_kunjungan, id_tiket))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
        flash("Tiket berhasil diupdate.", "success")
        return redirect(url_for("admin_tiket_page"))

    try:
        cursor.execute("SELECT * FROM tiket WHERE id_tiket=%s", (id_tiket,))
        tiket = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    return render_template("edit_tiket.html", tiket=tiket)

@app.route("/admin/user")
@login_required_admin
def admin_user():
    page = int(request.args.get("page", 1))
    per_page = 100
    offset = (page-1)*per_page

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM pelanggan")
        total_items = cursor.fetchone()["total"]
        total_pages = ceil(total_items / per_page)

        cursor.execute(
            "SELECT id_pelanggan, nama, username, email, tanggal_daftar FROM pelanggan "
            "ORDER BY id_pelanggan DESC LIMIT %s OFFSET %s",
            (per_page, offset)
        )

        users = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "admin.html",
        section="user",
        username=session.get("admin_username"),
        users=users,
        page=page,
        total_pages=total_pages
    )

@app.route("/admin/user/delete/<int:id_user>")
@login_required_admin
def admin_delete_user(id_user):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM pelanggan WHERE id_pelanggan=%s", (id_user,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    flash("User berhasil dihapus.", "success")
    return redirect(url_for("admin_user"))

@app.route("/admin/user/edit/<int:id_user>", methods=["GET","POST"])
@login_required_admin
def admin_edit_user(id_user):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        nama = request.form["nama"]
        username = request.form["username"]
        email = request.form["email"]
        try:
            cursor.execute("""
                UPDATE pelanggan SET nama=%s, username=%s, email=%s WHERE id_pelanggan=%s
            """, (nama, username, email, id_user))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
        flash("User berhasil diupdate.", "success")
        return redirect(url_for("admin_user"))

    try:
        cursor.execute("SELECT * FROM pelanggan WHERE id_pelanggan=%s", (id_user,))
        user = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    return render_template("edit_user.html", user=user)

@app.route("/admin/settings", methods=["GET","POST"])
@login_required_admin
def admin_settings():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        cursor.execute("SELECT password FROM admin WHERE id_admin=%s", (session['admin_id'],))
        current_password_hash = cursor.fetchone()['password']

        if not bcrypt.checkpw(old_password.encode('utf-8'), current_password_hash.encode('utf-8')):
            flash("Password lama salah.", "danger")
        elif new_password != confirm_password:
            flash("Password baru tidak cocok.", "danger")
        else:
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE admin SET password=%s WHERE id_admin=%s", (hashed, session['admin_id']))
            conn.commit()
            flash("Password berhasil diupdate.", "success")
    cursor.close()
    conn.close()
    return render_template("admin.html", section="settings", username=session.get("admin_username"))

@app.route("/admin/destinasi", methods=["GET", "POST"])
@login_required_admin
def admin_destinasi():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if request.method == "POST":
            nama = request.form.get("nama")
            lokasi = request.form.get("lokasi")
            deskripsi = request.form.get("deskripsi")
            jam_buka = request.form.get("jam_buka")
            harga = request.form.get("harga")
            gambar = request.form.get("gambar")

            cursor.execute("""
                INSERT INTO destinasi (nama, lokasi, deskripsi, jam_buka, harga, gambar)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nama, lokasi, deskripsi, jam_buka, harga, gambar))

            conn.commit()
            flash("Destinasi berhasil ditambahkan!", "success")
            return redirect(url_for("admin_destinasi"))

        cursor.execute("SELECT * FROM destinasi ORDER BY id_destinasi DESC")
        destinasi_list = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "admin.html",
        section="destinasi",
        destinasi_list=destinasi_list,
        username=session.get("admin_username")
    )

@app.route("/admin/destinasi/delete/<int:id_destinasi>")
@login_required_admin
def admin_delete_destinasi(id_destinasi):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM destinasi WHERE id_destinasi=%s", (id_destinasi,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    flash("Destinasi berhasil dihapus.", "success")
    return redirect(url_for("admin_destinasi"))

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