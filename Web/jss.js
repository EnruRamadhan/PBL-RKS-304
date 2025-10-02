const hargaDestinasi = {
  "Pantai Nongsa": 50000,
  "Pantai Marina": 40000,
  "Pantai Melayu": 45000,
  "Taman Rusa": 30000,
  "Kampung Vietnam": 35000,
  "Mata Kucing": 25000,
  "Ocarina Park": 60000
};

// Update preview harga otomatis
function updatePreviewHarga() {
  const destinasi = document.getElementById("destinasiSelect").value;
  const jumlah = parseInt(document.getElementById("jumlah").value) || 0;
  const harga = hargaDestinasi[destinasi] || 0;
  const total = harga * jumlah;

  document.getElementById("previewHarga").innerText =
    destinasi && jumlah > 0
      ? `Total Harga: Rp${total.toLocaleString()}`
      : "";
}

// Checkout langsung
function checkout() {
  const tanggal = document.getElementById("tanggal").value;
  const destinasi = document.getElementById("destinasiSelect").value;
  const jumlah = parseInt(document.getElementById("jumlah").value) || 0;
  const harga = hargaDestinasi[destinasi] || 0;
  const total = harga * jumlah;

  const hasilBox = document.getElementById("hasilBox");
  const hasilBooking = document.getElementById("hasilBooking");

  if (!tanggal || !destinasi || jumlah < 1) {
    hasilBooking.innerText = "⚠️ Silakan isi semua data booking terlebih dahulu!";
    hasilBox.classList.remove("hidden");
    return;
  }

  let pesan = "=== Bukti Pemesanan ===\n";
  pesan += `Destinasi  : ${destinasi}\n`;
  pesan += `Tanggal    : ${tanggal}\n`;
  pesan += `Jumlah     : ${jumlah} tiket\n`;
  pesan += `Total Bayar: Rp${total.toLocaleString()}\n`;
  pesan += "\nSilakan upload bukti pembayaran di bawah.";

  hasilBooking.innerText = pesan;
  hasilBox.classList.remove("hidden");
}

// Event listener preview harga
document.getElementById("destinasiSelect").addEventListener("change", updatePreviewHarga);
document.getElementById("jumlah").addEventListener("input", updatePreviewHarga);
document.getElementById("tanggal").addEventListener("change", updatePreviewHarga);

// Preview gambar setelah upload bukti pembayaran
document.getElementById("buktiPembayaran").addEventListener("change", function () {
  const file = this.files[0];
  const preview = document.getElementById("previewBukti");

  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      preview.innerHTML = `<img src="${e.target.result}" alt="Bukti Pembayaran" class="w-64 mt-2 rounded shadow">`;
    };
    reader.readAsDataURL(file);
  } else {
    preview.innerHTML = "";
  }
});
