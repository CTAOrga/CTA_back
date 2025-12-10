import http from "k6/http";
import { check, sleep } from "k6";

// 1) Configuración del escenario de carga
export const options = {
  stages: [
    { duration: "30s", target: 10 }, // subimos hasta 10 usuarios virtuales
    { duration: "2m", target: 10 }, // mantenemos 10 usuarios durante 2 minutos
    { duration: "30s", target: 0 }, // bajamos a 0
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"], // menos del 1% de requests con error
    http_req_duration: ["p(95)<800"], // el 95% responde en < 800 ms
  },
  noConnectionReuse: false,
  insecureSkipTLSVerify: true,
};

// 2) Base URL de la API (parametrizada)
// ⚠️ Este test va contra la BD DEMO (entorno "normal").
// En CI, el job k6-demo setea API_BASE_URL con la URL del backend DEMO.
const BASE_URL = __ENV.API_BASE_URL || "http://127.0.0.1:8000/api/v1";

// 3) Algunos términos de búsqueda típicos del catálogo
const searchTerms = ["", "peugeot", "fiat", "toyota", "cronos", "208"];

export default function () {
  // 4) Elegimos un término de búsqueda al azar
  const q = searchTerms[Math.floor(Math.random() * searchTerms.length)];

  // 5) Simulamos que el usuario navega por distintas páginas
  const page = Math.floor(Math.random() * 3) + 1; // páginas 1,2,3
  const pageSize = 20;

  // 6) Armamos la URL con query params
  let url = `${BASE_URL}/listings?page=${page}&page_size=${pageSize}`;
  if (q) {
    url += `&q=${encodeURIComponent(q)}`;
  }

  // 7) Hacemos la request HTTP GET
  const res = http.get(url);

  // 8) Validamos que la respuesta sea 200 OK
  check(res, {
    "status es 200": (r) => r.status === 200,
  });

  // 9) Pausa corta para simular "pensar/clickear"
  sleep(0.5);
}
