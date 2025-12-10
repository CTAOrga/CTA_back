// k6/auth.js
//
// Helper común para loguear usuarios contra la API de CTA.
// Usa /auth/login y devuelve el access_token (JWT).
//
// ⚠ Si tu endpoint de login usa form-data en vez de JSON,
//   podés adaptar el payload/comentado más abajo.

import http from "k6/http";

export function login({ baseUrl, email, password }) {
  const url = `${baseUrl}/auth/login`;

  // --- Variante JSON (ajustar si usás otra) ---
  const payload = JSON.stringify({
    email: email,
    password: password,
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  // --- Variante form-url-encoded (por si usás OAuth2PasswordRequestForm) ---
  // const payload = {
  //   username: email,
  //   password: password,
  // };
  // const params = {
  //   headers: { "Content-Type": "application/x-www-form-urlencoded" },
  // };

  const res = http.post(url, payload, params);

  if (res.status !== 200) {
    throw new Error(
      `Login failed for ${email}. status=${res.status} body=${res.body}`
    );
  }

  let body;
  try {
    body = res.json();
  } catch (e) {
    throw new Error(`No se pudo parsear JSON de /auth/login: ${e}`);
  }

  const token = body.access_token;
  if (!token) {
    throw new Error(
      `Respuesta de /auth/login no contiene access_token para ${email}`
    );
  }

  return token;
}
