import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  // Spike: subida brusca y bajada
  stages: [
    { duration: "10s", target: 1 }, // calentamiento suave
    { duration: "5s", target: 100 }, // subida muy rápida
    { duration: "20s", target: 100 }, // mantener pico
    { duration: "10s", target: 0 }, // bajar a 0
  ],
  thresholds: {
    http_req_failed: ["rate<0.05"], // tolera hasta 5% de errores en el pico
    http_req_duration: ["p(95)<1500"], // 95% < 1.5s
  },
  noConnectionReuse: false,
  insecureSkipTLSVerify: true,
};

// ⚠️ Este test va contra la BD DEMO (entorno "normal")
// En CI, el job k6-demo setea API_BASE_URL con la URL del backend DEMO.
const BASE_URL = __ENV.API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export default function () {
  const res = http.get(`${BASE_URL}/listings?page=1&page_size=20`);

  check(res, {
    "status 200": (r) => r.status === 200,
  });

  sleep(0.5);
}
