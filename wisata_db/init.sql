CREATE DATABASE IF NOT EXISTS wisata_db;
USE wisata_db;

-- Table Admin
CREATE TABLE admin (
  id_admin INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(100) NOT NULL,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role ENUM('superadmin', 'staff') DEFAULT 'staff'
);

-- Table Pengelola
CREATE TABLE pengelola (
  id_pengelola INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(100) NOT NULL,
  kontak VARCHAR(20),
  email VARCHAR(100),
  password VARCHAR(255),
  tanggal_daftar DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table Pantai
CREATE TABLE pantai (
  id_pantai INT AUTO_INCREMENT PRIMARY KEY,
  nama_pantai VARCHAR(100) NOT NULL,
  harga_tiket INT NOT NULL,
  jam_buka VARCHAR(50),
  deskripsi TEXT,
  foto_url VARCHAR(255),
  id_pengelola INT,
  FOREIGN KEY (id_pengelola) REFERENCES pengelola(id_pengelola)
    ON DELETE SET NULL ON UPDATE CASCADE
);

-- Table Pelanggan
CREATE TABLE pelanggan (
  id_pelanggan INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  no_hp VARCHAR(20),
  tanggal_daftar DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table Kunjungan
CREATE TABLE kunjungan (
  id_kunjungan INT AUTO_INCREMENT PRIMARY KEY,
  id_pelanggan INT,
  id_pantai INT,
  tanggal_kunjungan DATE DEFAULT (CURRENT_DATE),
  FOREIGN KEY (id_pelanggan) REFERENCES pelanggan(id_pelanggan)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_pantai) REFERENCES pantai(id_pantai)
    ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tambahkan data pantai contoh
INSERT INTO pantai (nama_pantai, harga_tiket, jam_buka, deskripsi, foto_url)
VALUES
('Pantai Nongsa', 10000, '24 Jam', 'Pantai populer untuk bersantai dan menikmati matahari terbenam di Batam.', 'https://example.com/nongsa.jpg'),
('Pantai Melayu', 15000, '07.00 - 18.00', 'Pantai luas dengan pasir putih halus dan ombak tenang, cocok untuk keluarga.', 'https://example.com/melayu.jpg'),
('Pantai Vio-Vio', 10000, '08.00 - 18.00', 'Spot foto instagramable dan snorkeling yang indah.', 'https://example.com/viovio.jpg');
