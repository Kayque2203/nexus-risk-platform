import { login, setToken, getToken } from "../api/client.js";

// Se ja existe um token salvo, nao faz sentido mostrar a tela de login --
// manda direto para a area logada.
if (getToken()) {
  window.location.href = "app.html";
}

const form = document.getElementById("login-form");
const errorBox = document.getElementById("form-error");
const submitBtn = document.getElementById("submit-btn");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  errorBox.classList.remove("visible");
  submitBtn.disabled = true;
  submitBtn.textContent = "Entrando...";

  try {
    const { access_token } = await login(email, password);
    setToken(access_token);
    window.location.href = "app.html";
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.classList.add("visible");
    submitBtn.disabled = false;
    submitBtn.textContent = "Entrar";
  }
});
