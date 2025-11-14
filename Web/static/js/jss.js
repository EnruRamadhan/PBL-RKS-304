let sudahCheckout = false;
let sudahUpload = false;

// 💰 Daftar harga destinasi
const hargaList = {
  "Pantai Nongsa": 10000,
  "Pantai Melayu": 15000,
  "Pantai Vio-Vio": 10000,
  "Pantai Elyora": 10000,
  "Pantai Marina": 20000,
  "Pantai Melur": 5000,
  "Taman Rusa": 5000,
  "Kampung Vietnam": 20000,
  "Mata Kucing": 10000,
  "Ocarina Park": 25000,
};

// 🧮 Update total harga otomatis
function updateTotalHarga() {
  const destinasi = document.getElementById("destinasiSelect").value;
  const jumlah = parseInt(document.getElementById("jumlah").value) || 0;
  const harga = hargaList[destinasi] || 0;
  const total = harga * jumlah;

  const previewHarga = document.getElementById("previewHarga");
  if (destinasi && jumlah > 0) {
    previewHarga.innerText = `Total Harga: Rp${total.toLocaleString("id-ID")}`;
  } else {
    previewHarga.innerText = "";
  }
}

// 🧾 Checkout
function checkout() {
  const namaPemesan = document.getElementById("namaPemesan").value.trim();
  const destinasi = document.getElementById("destinasiSelect").value;
  const tanggal = document.getElementById("tanggal").value;
  const jumlah = parseInt(document.getElementById("jumlah").value) || 0;

  if (!namaPemesan || !destinasi || !tanggal || jumlah < 1) {
    alert("⚠️ Lengkapi semua data pemesanan!");
    return;
  }

  const harga = hargaList[destinasi] || 0;
  const total = harga * jumlah;

  localStorage.setItem("namaUser", namaPemesan);

  document.getElementById("hasilBooking").innerText =
    `Bukti Pemesanan Tiket Wisata\n\n` +
    `Nama Pemesan: ${namaPemesan}\n` +
    `Destinasi: ${destinasi}\n` +
    `Tanggal: ${tanggal}\n` +
    `Jumlah Tiket: ${jumlah}\n` +
    `Harga per Tiket: Rp${harga.toLocaleString()}\n` +
    `Total Bayar: Rp${total.toLocaleString()}`;

  document.getElementById("hasilBox").classList.remove("hidden");
  sudahCheckout = true;

  // === Kirim ke backend Flask ===
  fetch("/checkout", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      nama_tiket: destinasi,
      jumlah: jumlah,
      harga: harga
    })
  })
  .then(res => res.json())
  .then(data => {
    console.log("Berhasil simpan ke database:", data);
  })
  .catch(err => {
    console.error("Error kirim ke server:", err);
  });

  alert("✅ Checkout berhasil! Silakan upload bukti pembayaran.");
}

// 📤 Upload bukti pembayaran
document.getElementById("buktiPembayaran").addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    const fileName = e.target.files[0].name;
    document.getElementById("previewBukti").innerHTML =
      `<p class='text-sm text-pink-600'>📎 ${fileName} berhasil diunggah.</p>`;
    sudahUpload = true;
  }
});

/// 📥 Download bukti pemesanan (versi aesthetic pink pastel & nama user otomatis)
function downloadBukti() {
  if (!sudahCheckout) {
    alert("⚠️ Silakan lakukan checkout terlebih dahulu!");
    return;
  }
  if (!sudahUpload) {
    alert("⚠️ Silakan upload bukti pembayaran terlebih dahulu!");
    return;
  }

  // 🧾 Ambil data user & form
  const namaUser = localStorage.getItem("namaUser")?.trim() || "Nama Pemesan";
  const destinasi = document.getElementById("destinasiSelect")?.value || "-";
  const tanggalRaw = document.getElementById("tanggal")?.value || "-";
  const tanggal = tanggalRaw !== "-" 
    ? new Date(tanggalRaw).toLocaleDateString('id-ID', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }) 
    : "-";
  const jumlahTiket = parseInt(document.getElementById("jumlah")?.value) || 0;
  const hargaTiket = hargaList[destinasi] || 0;
  const totalBayar = hargaTiket * jumlahTiket;

  // 🧩 Pastikan jsPDF tersedia
  if (!window.jspdf || !window.jspdf.jsPDF) {
    alert("⚠️ jsPDF belum ter-load! Pastikan CDN jsPDF sudah ditambahkan di file HTML kamu.");
    return;
  }

  // ✨ Buat PDF baru
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF("p", "mm", "a4");

  // 🎀 Header
  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.setTextColor(234, 84, 128);
  doc.text("BUKTI PEMESANAN TIKET WISATA", 105, 25, { align: "center" });

  doc.setDrawColor(255, 182, 193);
  doc.line(20, 30, 190, 30);

  // 🕒 Waktu cetak
  const waktuCetak = new Date().toLocaleString("id-ID", {
    dateStyle: "long",
    timeStyle: "short",
  });
  doc.setFont("helvetica", "italic");
  doc.setFontSize(10);
  doc.setTextColor(100, 100, 100);
  doc.text(`Dicetak pada: ${waktuCetak}`, 20, 38);

  // 🩷 Ucapan terima kasih
  doc.setFont("helvetica", "normal");
  doc.setFontSize(12);
  doc.setTextColor(0, 0, 0);
  doc.text(`Terima kasih, ${namaUser}!`, 20, 52);
  doc.text("Telah mempercayakan perjalanan wisatanya bersama kami.", 20, 59);

  // 📋 Detail Pemesanan
  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.setTextColor(50, 50, 50);
  doc.text("Detail Pemesanan:", 20, 75);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(12);
  let y = 85;
  const detail = [
    ["Nama Pemesan", namaUser],
    ["Destinasi", destinasi],
    ["Tanggal Kunjungan", tanggal],
    ["Jumlah Tiket", jumlahTiket.toString()],
    ["Harga per Tiket", `Rp${hargaTiket.toLocaleString("id-ID")}`],
    ["Total Bayar", `Rp${totalBayar.toLocaleString("id-ID")}`],
  ];
  detail.forEach(([label, value]) => {
    doc.text(`${label}:`, 25, y);
    doc.text(value, 90, y);
    y += 9;
  });

  // 📝 Catatan
  y += 10;
  doc.setFont("helvetica", "italic");
  doc.setTextColor(90, 90, 90);
  doc.text("Catatan:", 20, y);
  y += 6;
  const notes = [
    "• Simpan bukti ini sebagai tanda sah pemesanan tiket.",
    "• Harap tunjukkan bukti ini kepada petugas saat check-in.",
    "• Pembatalan tiket mengikuti kebijakan pengelola destinasi.",
  ];
  notes.forEach((n) => {
    doc.text(n, 25, y);
    y += 6;
  });

  // 🪷 Footer
  doc.setDrawColor(255, 182, 193);
  doc.line(20, 280, 190, 280);
  doc.setFontSize(10);
  doc.setTextColor(234, 84, 128);
  doc.text("PBL RKS-304 | Sistem Informasi Destinasi Wisata", 105, 287, {
    align: "center",
  });

  // 💾 Simpan PDF
  const namaFile = `Bukti_Pemesanan_${destinasi.replace(/\s+/g, "_")}.pdf`;
  doc.save(namaFile);
  alert("✅ Bukti pemesanan berhasil diunduh!");
}

// 🔎 Fitur pencarian destinasi
document.getElementById("searchInput").addEventListener("input", function () {
  const query = this.value.toLowerCase();
  const cards = document.querySelectorAll(".destinasi-card");
  cards.forEach((card) => {
    const title = card.querySelector("h3").innerText.toLowerCase();
    card.style.display = title.includes(query) ? "flex" : "none";
  });
});

// ⏱️ Update harga otomatis saat input berubah
document.getElementById("destinasiSelect").addEventListener("change", updateTotalHarga);
document.getElementById("jumlah").addEventListener("input", updateTotalHarga);
