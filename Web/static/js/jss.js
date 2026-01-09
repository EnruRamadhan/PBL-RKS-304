let sudahCheckout = false;
let sudahUpload = false;
let currentTiketID = null;

function updateTotalHarga() {
  const destinasi = document.getElementById("destinasiSelect").value;
  const jumlah = parseInt(document.getElementById("jumlah").value) || 0;
  const select = document.getElementById("destinasiSelect");
  const harga = parseInt(select.options[select.selectedIndex].dataset.harga)
  const total = harga * jumlah;
  const previewHarga = document.getElementById("previewHarga");
  if (destinasi && jumlah > 0) {
    previewHarga.innerText = `Total Harga: Rp${total.toLocaleString("id-ID")}`;
  } else {
    previewHarga.innerText = "";
  }
}

async function checkout() {
  const destinasiSelect = document.getElementById("destinasiSelect");
  const destinasi = destinasiSelect.value;
  const harga = parseInt(destinasiSelect.options[destinasiSelect.selectedIndex].dataset.harga);
  const tanggal = document.getElementById("tanggal").value;
  const jumlah = parseInt(document.getElementById("jumlah").value);
  const namaPemesan = document.getElementById("namaPemesan").value.trim();

  if (!namaPemesan || !destinasi || !tanggal || jumlah < 1) {
    alert("Lengkapi semua data!");
    return;
  }

  const res = await fetch("/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nama_tiket: destinasi,
      jumlah,
      harga,
      tanggal
    })
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.error);
    return;
  }

  currentTiketID = data.tiket_id;
  sudahCheckout = true;

  document.getElementById("buktiPembayaran").disabled = false;
  document.getElementById("btnUpload").disabled = false;

  alert("Checkout berhasil! Silakan upload bukti pembayaran.");
}

async function uploadBukti() {
  if (!currentTiketID) {
    alert("Tiket ID tidak ditemukan! Checkout dulu.");
    return;
  }

  const fileInput = document.getElementById("buktiPembayaran");
  const file = fileInput.files[0];

  if (!file) {
    alert("Pilih file bukti pembayaran!");
    return;
  }

  const fd = new FormData();
  fd.append("bukti", file);
  fd.append("tiket_id", currentTiketID);

  const res = await fetch("/upload_bukti", {
    method: "POST",
    body: fd
  });

  const data = await res.json();

  if (res.ok) {
    sudahUpload = true;
    alert("✅ Bukti berhasil diupload! Sekarang Anda bisa download bukti pemesanan.");
  } else {
    alert("❌ Upload gagal: " + data.error);
  }
}

function downloadBukti() {
  if (!sudahCheckout) {
    alert("⚠️ Silakan lakukan checkout terlebih dahulu!");
    return;
  }
  if (!sudahUpload) {
    alert("⚠️ Silakan upload bukti pembayaran terlebih dahulu!");
    return;
  }

  const namaUser = document.getElementById("namaPemesan").value.trim() || "Nama Pemesan";
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
  const hargaTiket = parseInt(
    document.querySelector(`#destinasiSelect option[value="${destinasi}"]`)?.dataset.harga
  ) || 0;
  const totalBayar = hargaTiket * jumlahTiket;

  if (!window.jspdf || !window.jspdf.jsPDF) {
    alert("⚠️ jsPDF belum ter-load! Pastikan CDN jsPDF sudah ditambahkan di file HTML kamu.");
    return;
  }

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF("p", "mm", "a4");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.setTextColor(234, 84, 128);
  doc.text("BUKTI PEMESANAN TIKET WISATA", 105, 25, { align: "center" });

  doc.setDrawColor(255, 182, 193);
  doc.line(20, 30, 190, 30);

  const waktuCetak = new Date().toLocaleString("id-ID", {
    dateStyle: "long",
    timeStyle: "short",
  });
  doc.setFont("helvetica", "italic");
  doc.setFontSize(10);
  doc.setTextColor(100, 100, 100);
  doc.text(`Dicetak pada: ${waktuCetak}`, 20, 38);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(12);
  doc.setTextColor(0, 0, 0);
  doc.text(`Terima kasih, ${namaUser}!`, 20, 52);
  doc.text("Telah mempercayakan perjalanan wisatanya bersama kami.", 20, 59);

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

  doc.setDrawColor(255, 182, 193);
  doc.line(20, 280, 190, 280);
  doc.setFontSize(10);
  doc.setTextColor(234, 84, 128);
  doc.text("PBL RKS-304 | Sistem Informasi Destinasi Wisata", 105, 287, {
    align: "center",
  });

  const namaFile = `Bukti_Pemesanan_${destinasi.replace(/\s+/g, "_")}.pdf`;
  doc.save(namaFile);
  
  // ⭐ AUTO RESET SETELAH DOWNLOAD SELESAI ⭐
  autoResetForm();
  
  alert("✅ Bukti pemesanan berhasil diunduh! Form telah direset untuk pemesanan baru.");
}

// ⭐ FUNGSI AUTO RESET SETELAH DOWNLOAD ⭐
function autoResetForm() {
  // Reset semua variabel
  currentTiketID = null;
  sudahUpload = false;
  sudahCheckout = false;

  // Kosongkan semua input form
  document.getElementById("buktiPembayaran").value = "";
  document.getElementById("namaPemesan").value = "";
  document.getElementById("destinasiSelect").value = "";
  document.getElementById("tanggal").value = "";
  document.getElementById("jumlah").value = "";
  document.getElementById("previewHarga").innerText = "";
  
  // Nonaktifkan tombol upload
  document.getElementById("buktiPembayaran").disabled = true;
  document.getElementById("btnUpload").disabled = true;
}

document.getElementById("searchInput").addEventListener("input", function () {
  const query = this.value.toLowerCase();
  const cards = document.querySelectorAll(".destinasi-card");
  cards.forEach((card) => {
    const title = card.querySelector("h3").innerText.toLowerCase();
    card.style.display = title.includes(query) ? "flex" : "none";
  });
});

document.getElementById('jumlah').addEventListener('input', hitungTotal);
document.getElementById('destinasiSelect').addEventListener('change', hitungTotal);

function hitungTotal() {
    let select = document.getElementById('destinasiSelect');
    let jumlah = document.getElementById('jumlah').value;

    let harga = select.options[select.selectedIndex].getAttribute('data-harga');

    if (harga && jumlah) {
        let total = parseInt(harga) * parseInt(jumlah);
        document.getElementById('previewHarga').innerText =
            "Total: Rp" + total.toLocaleString("id-ID");
    } else {
        document.getElementById('previewHarga').innerText = "";
    }
}