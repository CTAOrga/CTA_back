import http from "k6/http";
import { check, sleep } from "k6";
import { login } from "./auth.js";

// 1) Escenario de Stress para reportes admin
export const options = {
  stages: [
    { duration: "30s", target: 5 }, // pocos admins consultando
    { duration: "1m", target: 20 }, // carga moderada
    { duration: "1m", target: 50 }, // carga alta de reportes
    { duration: "30s", target: 0 }, // bajamos
  ],
  thresholds: {
    http_req_failed: ["rate<0.05"], // toleramos hasta 5% de fallos en stress
    http_req_duration: ["p(95)<2000"], // 95% < 2s porque los reportes pueden ser pesados
  },
  noConnectionReuse: false,
  insecureSkipTLSVerify: true,
};

// 2) API y credenciales admin parametrizadas por variables de entorno
// ⚠️ Este test va contra la BD DEMO (entorno "normal")
const BASE_URL = __ENV.API_BASE_URL || "http://127.0.0.1:8000/api/v1";

const ADMIN_EMAIL = __ENV.ADMIN_EMAIL || "";
const ADMIN_PASSWORD = __ENV.ADMIN_PASSWORD || "";

// 3) Opcional: distintos rangos de fechas para no siempre pegar igual
const dateRanges = [
  { from: "", to: "" }, // sin filtro de fechas
  { from: "2024-01-01", to: "2024-12-31" },
  { from: "2025-01-01", to: "2025-12-31" },
];

// ----------------------------------------------------------
// setup(): se ejecuta UNA sola vez antes del escenario.
// - Hace login del admin y obtiene un access_token fresco.
// ----------------------------------------------------------
export function setup() {
  if (!ADMIN_EMAIL || !ADMIN_PASSWORD) {
    throw new Error(
      "Faltan ADMIN_EMAIL o ADMIN_PASSWORD. Definilos en las variables de entorno."
    );
  }

  const adminToken = login({
    baseUrl: BASE_URL,
    email: ADMIN_EMAIL,
    password: ADMIN_PASSWORD,
  });

  return { adminToken };
}

// ----------------------------------------------------------
// default(data): cada VU, cada iteración.
// - Usa el adminToken para consultar /admin/reports/top-sold-cars
//   con distintos filtros de fecha.
// ----------------------------------------------------------
export default function (data) {
  const adminToken = data.adminToken;

  if (!adminToken) {
    console.error(
      "adminToken no disponible en data. Revisá el setup() de stress-admin-reports.js."
    );
    return;
  }

  // 4) Elegimos un rango de fechas al azar
  const range = dateRanges[Math.floor(Math.random() * dateRanges.length)];

  // 5) Armamos query params
  const params = [];
  if (range.from) params.push(`date_from=${range.from}`);
  if (range.to) params.push(`date_to=${range.to}`);
  const queryString = params.length > 0 ? `?${params.join("&")}` : "";

  const url = `${BASE_URL}/admin/reports/top-sold-cars${queryString}`;

  // 6) Headers con Authorization
  const headers = {
    Authorization: `Bearer ${adminToken}`,
  };

  // 7) Request al endpoint de reporte
  const res = http.get(url, { headers });

  // 8) Checks básicos
  check(res, {
    "status es 200": (r) => r.status === 200,
    "respuesta es JSON": (r) =>
      r.headers["Content-Type"]?.includes("application/json"),
  });

  // 9) Pausa muy corta: admins refrescando reportes
  sleep(0.5);
}
