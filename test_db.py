import mysql.connector

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root123",
    "database": "wisata_db",
    "port": 3306,  # Ganti ke 3306
    "auth_plugin": "mysql_native_password"
}

try:
    conn = mysql.connector.connect(**db_config)
    print("✅ Koneksi database BERHASIL!")
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Tables:", tables)
    conn.close()
except Exception as e:
    print("❌ Koneksi database GAGAL:", e)