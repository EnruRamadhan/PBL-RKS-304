import mysql.connector
import bcrypt

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root123",
    "database": "wisata_db",
    "port": 3306,
    "auth_plugin": "mysql_native_password"
}

# Test insert manual
def test_registration():
    username = "test_manual"
    email = "test_manual@email.com"
    password = "password123"
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO pelanggan (nama, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()
        print("✅ Manual insert BERHASIL!")
        
        # Verify
        cursor.execute("SELECT * FROM pelanggan WHERE email = %s", (email,))
        user = cursor.fetchone()
        print(f"✅ User found: {user}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Manual insert GAGAL: {e}")

test_registration()