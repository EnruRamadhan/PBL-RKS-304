// ======== Navbar Scroll Effect ========
const navbar = document.getElementById("navbar");

window.addEventListener("scroll", () => {
  if (window.scrollY > 60) {
    navbar.classList.add("navbar-scrolled");
  } else {
    navbar.classList.remove("navbar-scrolled");
  }
});

// ======== Background Slideshow ========
const slides = document.querySelectorAll(".slide");
let currentSlide = 0;

// Pastikan slide pertama aktif dari awal
slides[currentSlide].classList.add("active");

// Fungsi ganti slide
function nextSlide() {
  // Hilangkan slide aktif sekarang
  slides[currentSlide].classList.remove("active");

  // Pindah ke slide berikutnya
  currentSlide = (currentSlide + 1) % slides.length;

  // Aktifkan slide baru
  slides[currentSlide].classList.add("active");
}

// Ganti slide setiap 5 detik
setInterval(nextSlide, 3000);

// ======== Preload Semua Gambar (biar gak abu-abu) ========
slides.forEach(slide => {
  const img = new Image();
  const bg = slide.style.backgroundImage.slice(5, -2); // ambil URL di background-image
  img.src = bg;
});
