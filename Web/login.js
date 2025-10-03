const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginMessage = document.getElementById('loginMessage');

// Fungsi untuk toggle password visibility
function togglePasswordVisibility() {
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
  } else {
    passwordInput.type = "password";
  }
}

// Tambahkan klik pada ikon gembok
const lockIcon = document.querySelector('.fa-lock');
lockIcon.style.cursor = "pointer";
lockIcon.addEventListener('click', togglePasswordVisibility);

// Fungsi untuk cek kekuatan password
function isStrongPassword(password) {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSymbol = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  return password.length >= minLength && hasUpperCase && hasLowerCase && hasNumber && hasSymbol;
}

// Event submit form
loginForm.addEventListener('submit', function(e) {
  e.preventDefault();

  const username = usernameInput.value.trim();
  const password = passwordInput.value;

  // Validasi password kuat
  if (!isStrongPassword(password)) {
    loginMessage.style.color = 'red';
    loginMessage.textContent = "Password harus minimal 8 karakter, mengandung huruf besar, huruf kecil, angka, dan simbol!";
    return;
  }

   // Ambil data user dari localStorage (hasil register)
  const savedPassword = localStorage.getItem(username);

  if (savedPassword && savedPassword === password) {
    loginMessage.style.color = 'green';
    loginMessage.textContent = "Login berhasil! Mengarahkan...";
    
    // Simpan sesi login
    localStorage.setItem("loggedInUser", username);

    setTimeout(() => {
      window.location.href = "index.html"; 
    }, 1500);
  } else {
    loginMessage.style.color = 'red';
    loginMessage.textContent = "Username atau password salah!";
  }
});