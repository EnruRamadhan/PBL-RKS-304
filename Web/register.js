const registerForm = document.getElementById("registerForm");
const regUsername = document.getElementById("regUsername");
const regEmail = document.getElementById("regEmail");
const regPassword = document.getElementById("regPassword");
const regConfirm = document.getElementById("regConfirm");
const registerMessage = document.getElementById("registerMessage");

// fungsi validasi password kuat
function isStrongPassword(password) {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSymbol = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  return password.length >= minLength && hasUpperCase && hasLowerCase && hasNumber && hasSymbol;
}

registerForm.addEventListener("submit", function(e) {
  e.preventDefault();

  const username = regUsername.value.trim();
  const email = regEmail.value.trim();
  const password = regPassword.value;
  const confirm = regConfirm.value;

  if (password !== confirm) {
    registerMessage.style.color = "red";
    registerMessage.textContent = "Password dan konfirmasi tidak sama!";
    return;
  }

  if (!isStrongPassword(password)) {
    registerMessage.style.color = "red";
    registerMessage.textContent = "Password harus min 8 karakter, ada huruf besar, kecil, angka, simbol!";
    return;
  }

  // simpan ke localStorage
  localStorage.setItem(username, password);
  localStorage.setItem(username + "_email", email);

  registerMessage.style.color = "green";
  registerMessage.textContent = "Registrasi berhasil! Silakan login...";

  setTimeout(() => {
    window.location.href = "login.html";
  }, 1500);
});
