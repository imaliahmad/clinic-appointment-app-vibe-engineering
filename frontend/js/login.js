import { login } from "./api.js";

const PAGES = {
  receptionist: "/reception",
  doctor: "/doctor",
  admin: "/admin",
};

const form = document.getElementById("login-form");
const message = document.getElementById("message");
const button = form.querySelector("button");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  button.disabled = true;
  try {
    const result = await login(form.username.value.trim(), form.password.value);
    if (result.status) {
      window.location.href = PAGES[result.data.role] || "/";
    } else {
      message.textContent = result.message;
    }
  } catch (error) {
    message.textContent = "Could not reach the server";
  } finally {
    button.disabled = false;
  }
});
