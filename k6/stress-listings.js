import http from "k6/http";
import { check, sleep } from "k6";

// 1) Escenario de Stress: aumentamos carga en escalones
export const options = {
  stages: [
    { duration: "30s", target: 10 }, // carga baja
    { duration: "30s", target: 30 }, // carga moderada
    { duration: "30s", target: 60 }, // carga alta
    { duration: "30s", target: 100 }, // carga MUY alta
    { duration: "30s", target: 0 }, // descenso
  ],
  thresholds: {
    http_req_failed: ["rate<0.03"], // se tolera hasta 3% de fallos
    http_req_duration: ["p(95)<1500"], // 95% < 1.5s
  },
  noConnectionReuse: false,
  insecureSkipTLSVerify: true,
};

// 2) API parametrizada (⚠️ DEMO / BD "normal")
// En CI, el job k6-demo setea API_BASE_URL con la URL del backend DEMO.
// Localmente, si no hay env, cae en localhost.
const BASE_URL = __ENV.API_BASE_URL || "http://127.0.0.1:8000/api/v1";

// 3) Términos de búsqueda como en el test de carga
const searchTerms = ["", "peugeot", "fiat", "toyota", "cronos", "208"];

export default function () {
  // 4) Variación en búsquedas
  const q = searchTerms[Math.floor(Math.random() * searchTerms.length)];

  // 5) Variación en páginas
  const page = Math.floor(Math.random() * 3) + 1;
  const pageSize = 20;

  let url = `${BASE_URL}/listings?page=${page}&page_size=${pageSize}`;
  if (q) {
    url += `&q=${encodeURIComponent(q)}`;
  }

  // 6) Request
  const res = http.get(url);

  // 7) Checks de respuesta válida
  check(res, {
    "status es 200": (r) => r.status === 200,
  });

  // 8) Pausa mínima (mantener presión)
  sleep(0.3);
}
