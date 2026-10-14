import { getMe, logout } from "./api.js";

const usernameLabel = document.getElementById("username");
const logoutButton = document.getElementById("logout");

async function showUser() {
  const result = await getMe();
  if (result.status) {
    usernameLabel.textContent = result.data.username;
  }
}

logoutButton.addEventListener("click", async () => {
  await logout();
  window.location.href = "/";
});

showUser();
