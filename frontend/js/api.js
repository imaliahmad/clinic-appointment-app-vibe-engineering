// The only file that calls fetch(). One function per endpoint.
// Every function resolves to the JSON body: {status, message, data, errors}.
// 401 sends the browser to the login page; 403 sends it to the user's own page.

const PAGES = {
  receptionist: "/reception",
  doctor: "/doctor",
  admin: "/admin",
};

async function request(method, path, body, redirectOnAuthError = true) {
  const options = { method, headers: {} };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  const response = await fetch(path, options);
  if (redirectOnAuthError && response.status === 401) {
    window.location.href = "/";
  } else if (redirectOnAuthError && response.status === 403) {
    const me = await request("GET", "/api/auth/me");
    window.location.href = (me.data && PAGES[me.data.role]) || "/";
  }
  try {
    return await response.json();
  } catch (error) {
    return { status: false, message: "Unexpected server response", data: null, errors: [] };
  }
}

export function login(username, password) {
  // A wrong password is a normal 401 answer here: show it, do not redirect.
  return request("POST", "/api/auth/login", { username, password }, false);
}

export function logout() {
  return request("POST", "/api/auth/logout");
}

export function getMe() {
  return request("GET", "/api/auth/me");
}
