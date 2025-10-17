const loginForm = document.getElementById("loginForm");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const loginMessage = document.getElementById("loginMessage");
const togglePassword = document.getElementById("togglePassword");

// === TOMBOL SHOW/HIDE PASSWORD ===
togglePassword.addEventListener("click", () => {
  const isPasswordHidden = passwordInput.getAttribute("type") === "password";

  // Ubah tipe input
  passwordInput.setAttribute("type", isPasswordHidden ? "text" : "password");

  // Ubah ikon mata
  if (isPasswordHidden) {
    togglePassword.classList.remove("fa-eye");
    togglePassword.classList.add("fa-eye-slash");
  } else {
    togglePassword.classList.remove("fa-eye-slash");
    togglePassword.classList.add("fa-eye");
  }
});

// === CEK KEKUATAN PASSWORD ===
function isStrongPassword(password) {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSymbol = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  return (
    password.length >= minLength &&
    hasUpperCase &&
    hasLowerCase &&
    hasNumber &&
    hasSymbol
  );
}

// === EVENT LOGIN FORM ===
loginForm.addEventListener("submit", function (e) {
  e.preventDefault();

  const username = usernameInput.value.trim();
  const password = passwordInput.value;

  // Validasi password kuat
  if (!isStrongPassword(password)) {
    loginMessage.style.color = "red";
    loginMessage.textContent =
      "Password harus minimal 8 karakter, mengandung huruf besar, huruf kecil, angka, dan simbol!";
    return;
  }

  // Ambil data user dari localStorage
  const savedPassword = localStorage.getItem(username);

  if (savedPassword && savedPassword === password) {
    loginMessage.style.color = "green";
    loginMessage.textContent = "Login berhasil! Mengarahkan...";

    // Simpan sesi login
    localStorage.setItem("loggedInUser", username);

    setTimeout(() => {
      window.location.href = "/index";
    }, 1500);
  } else {
    loginMessage.style.color = "red";
    loginMessage.textContent = "Username atau password salah!";
  }
});

// === SLIDESHOW BACKGROUND ===
const slides = document.querySelectorAll(".background-slideshow .slide");
let currentSlide = 0;

function nextSlide() {
  slides[currentSlide].classList.remove("active");
  currentSlide = (currentSlide + 1) % slides.length;
  slides[currentSlide].classList.add("active");
}

setInterval(nextSlide, 5000); // ganti setiap 5 detik
