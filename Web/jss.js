function downloadBuktiTXT() {
  if (!buktiPesanan) {
    alert("Belum ada bukti pemesanan untuk diunduh!");
    return;
  }
  const blob = new Blob([buktiPesanan], { type: "text/plain" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "Bukti_Pemesanan.txt";
  link.click();
}

function downloadBuktiPDF() {
  if (!buktiPesanan) {
    alert("Belum ada bukti pemesanan untuk diunduh!");
    return;
  }
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  doc.setFont("helvetica", "normal");
  doc.setFontSize(14);

  // Tulis judul
  doc.text("Bukti Pemesanan Tiket Wisata", 20, 20);

  // Pisahkan baris agar rapi
  const lines = buktiPesanan.split("\n");
  let y = 40;
  lines.forEach(line => {
    doc.text(line, 20, y);
    y += 10;
  });

  // Simpan PDF
  doc.save("Bukti_Pemesanan.pdf");
}
