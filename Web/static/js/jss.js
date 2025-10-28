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
  const destinasi = document.getElementById("destinasiSelect").value;
  const tanggal = document.getElementById("tanggal").value;
  const jumlah = parseInt(document.getElementById("jumlah").value) || 0;

  if (!destinasi || !tanggal || jumlah < 1) {
    alert("⚠️ Lengkapi semua data pemesanan!");
    return;
  }

  const harga = hargaList[destinasi] || 0;
  const total = harga * jumlah;

  document.getElementById("hasilBooking").innerText =
    `Bukti Pemesanan Tiket Wisata\n\n` +
    `Destinasi: ${destinasi}\n` +
    `Tanggal: ${tanggal}\n` +
    `Jumlah Tiket: ${jumlah}\n` +
    `Harga per Tiket: Rp${harga.toLocaleString()}\n` +
    `Total Bayar: Rp${total.toLocaleString()}`;

  document.getElementById("hasilBox").classList.remove("hidden");
  sudahCheckout = true;
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

  // Ambil data user & form
  const namaUser = localStorage.getItem("namaUser") || "Nama Pemesan";
  const destinasi = document.getElementById("destinasiSelect")?.value || "-";
  const tanggalRaw = document.getElementById("tanggal")?.value || "-";
  const tanggal = tanggalRaw !== "-" 
    ? new Date(tanggalRaw).toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) 
    : "-";
  const jumlahTiket = document.getElementById("jumlahTiket")?.value || "-";
  const hargaTiket = document.getElementById("hargaTiket")?.value || "-";
  const totalBayar = jumlahTiket && hargaTiket ? jumlahTiket * hargaTiket : "-";

  if (!window.jspdf) {
    alert("⚠️ jsPDF belum ter-load!");
    return;
  }
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ orientation: "portrait", unit: "pt", format: "a4" });
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 40;

  // 🌸 Background pastel
  doc.setFillColor("#FFE4EC");
  doc.rect(0, 0, pageWidth, pageHeight, "F");

  // 🎀 Header
  doc.setFont("helvetica", "bold");
  doc.setFontSize(14);
  doc.setTextColor("#D46482");
  doc.text("BATAM TRAVEL", pageWidth / 2, 40, { align: "center" });

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.text("www.batamtravel.co.id | info@batamtravel.co.id | +62 812-3456-7890", pageWidth / 2, 55, { align: "center" });

  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.text("Bukti Pemesanan Tiket Wisata", pageWidth / 2, 80, { align: "center" });

  doc.setDrawColor("#D46482");
  doc.setLineWidth(1);
  doc.line(margin, 90, pageWidth - margin, 90);

  // 🧾 Detail Pemesanan di box
  let y = 110;
  doc.setDrawColor("#D46482");
  doc.setLineWidth(0.8);
  doc.rect(margin, y, pageWidth - 2 * margin, 120); // box detail

  doc.setFont("helvetica", "normal");
  doc.setFontSize(12);
  doc.setTextColor("#333");
  let textX = margin + 10;
  let textY = y + 25;
  doc.text(`Atas Nama       : ${namaUser}`, textX, textY);
  textY += 18;
  doc.text(`Destinasi       : ${destinasi}`, textX, textY);
  textY += 18;
  doc.text(`Tanggal Kunjungan: ${tanggal}`, textX, textY);
  textY += 18;
  doc.text(`Jumlah Tiket    : ${jumlahTiket}`, textX, textY);
  textY += 18;
  doc.text(`Harga per Tiket : Rp ${parseFloat(hargaTiket).toLocaleString('id-ID')}`, textX, textY);
  textY += 18;
  doc.text(`Total Bayar     : Rp ${parseFloat(totalBayar).toLocaleString('id-ID')}`, textX, textY);

  // 📋 Catatan Penting
  y += 140;
  const noteHeight = 120;
  doc.setFillColor("#FFD9E6");
  doc.roundedRect(margin, y, pageWidth - 2 * margin, noteHeight, 8, 8, "F");

  let noteY = y + 20;
  doc.setFont("helvetica", "bold");
  doc.setTextColor("#D46482");
  doc.text("Catatan Penting:", margin + 10, noteY);

  noteY += 18;
  doc.setFont("helvetica", "normal");
  doc.setTextColor("#333");
  const notes = [
    "Harap menunjukkan bukti pemesanan ini saat check-in di lokasi wisata.",
    "Tiket hanya berlaku pada tanggal yang tertera dan tidak dapat dipindah tangankan.",
    "Pembatalan atau perubahan jadwal dapat dilakukan maksimal 24 jam sebelum waktu kunjungan.",
    "Kebijakan refund mengikuti ketentuan yang berlaku di Batam Travel.",
    "Pastikan untuk tiba 15 menit sebelum waktu kunjungan untuk proses check-in."
  ];
  notes.forEach(note => {
    doc.text("• " + note, margin + 15, noteY);
    noteY += 16;
  });

  // 💬 Ucapan Terima Kasih
  noteY += 10;
  doc.setFont("helvetica", "italic");
  doc.setTextColor("#555");
  doc.text("Terima kasih telah memesan melalui platform kami.", margin + 10, noteY);
  noteY += 15;
  doc.text("Nikmati liburanmu dan tetap jaga kebersihan lingkungan.", margin + 10, noteY);

  // 🩷 Footer
  doc.setFontSize(10);
  doc.setTextColor("#D46482");
  doc.text("© 2025 Batam Travel | Semua hak dilindungi", pageWidth / 2, pageHeight - 30, { align: "center" });

  // Download PDF
  doc.save(`Bukti_Pemesanan_${namaUser.replace(/\s+/g, "_")}.pdf`);
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
