// k6/stress-purchases.js
// ----------------------------------------------------------
// Stress de COMPRAS construyendo TODO el escenario desde k6:
// - Lee /car-models para obtener modelos de auto (sembrados en seed_perf).
// - Con el usuario AGENCY (login) crea items de inventario.
// - Con ese inventario crea listings/ofertas.
// - Con el usuario BUYER (login) hace compras sobre esos listings bajo carga.
//
// ⚠️ Correr SIEMPRE contra la API que apunta a la BD PERF (cta_perf).
// ⚠️ Requiere credenciales:
//   - AGENCY_EMAIL / AGENCY_PASSWORD
//   - BUYER_EMAIL  / BUYER_PASSWORD
//   (tokens se generan en runtime vía /auth/login)
// ----------------------------------------------------------

import http from "k6/http";
import { check, sleep } from "k6";
import { login } from "./auth.js";

export const options = {
  stages: [
    { duration: "30s", target: 5 }, // pocos buyers comprando
    { duration: "1m", target: 20 }, // pico razonable
    { duration: "1m", target: 40 }, // stress fuerte
    { duration: "30s", target: 0 }, // bajamos
  ],
  thresholds: {
    // Permitimos hasta ~10% de fallos HTTP, pero con los stocks configurados
    // deberías estar mucho más abajo (2-4% aprox).
    http_req_failed: ["rate<0.10"],
    http_req_duration: ["p(95)<2000"],
  },
  noConnectionReuse: false,
  insecureSkipTLSVerify: true,
};

// Base URL: en CI vas a pasar API_BASE_URL apuntando a PERF.
// Localmente podés usar API_BASE_URL_PERF o caer en localhost.
const BASE_URL =
  __ENV.API_BASE_URL_PERF ||
  __ENV.API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";

// Credenciales de AGENCY / BUYER (por defecto las de seed_perf)
const AGENCY_EMAIL = __ENV.AGENCY_EMAIL || "agency_perf@cta.com";
const AGENCY_PASSWORD = __ENV.AGENCY_PASSWORD || "Perf1234!";
const BUYER_EMAIL = __ENV.BUYER_EMAIL || "buyer_perf@cta.com";
const BUYER_PASSWORD = __ENV.BUYER_PASSWORD || "Perf1234!";

const N_MODELS = 3; // cuántos car_models usamos para crear ofertas
const INVENTORY_QTY = 2200; // cantidad en inventario para cada modelo
const LISTING_STOCK = 2100; // stock inicial de cada oferta (<= INVENTORY_QTY)

// ----------------------------------------------------------
// setup(): se ejecuta UNA vez antes de todo el escenario.
// - Hace login de AGENCY y BUYER, obtiene sus tokens.
// - Lee car-models.
// - Crea inventario para algunos car_models.
// - Crea listings a partir de ese inventario.
// - Devuelve los IDs de listings y el buyerToken para default().
// ----------------------------------------------------------
export function setup() {
  // 0) Validar credenciales mínimas
  if (!AGENCY_EMAIL || !AGENCY_PASSWORD || !BUYER_EMAIL || !BUYER_PASSWORD) {
    throw new Error(
      "Faltan AGENCY_EMAIL/AGENCY_PASSWORD o BUYER_EMAIL/BUYER_PASSWORD en el entorno."
    );
  }

  // 1) Login de AGENCY y BUYER contra la API PERF
  const agencyToken = login({
    baseUrl: BASE_URL,
    email: AGENCY_EMAIL,
    password: AGENCY_PASSWORD,
  });

  const buyerToken = login({
    baseUrl: BASE_URL,
    email: BUYER_EMAIL,
    password: BUYER_PASSWORD,
  });

  const agencyHeaders = {
    Authorization: `Bearer ${agencyToken}`,
    "Content-Type": "application/json",
  };

  // 2) Leer car-models de la BD PERF (sembrados por seed_perf)
  const carModelsRes = http.get(`${BASE_URL}/car-models?page=1&page_size=50`, {
    headers: agencyHeaders,
  });

  check(carModelsRes, {
    "GET /car-models 200": (r) => r.status === 200,
  });

  let carModels;
  try {
    carModels = carModelsRes.json();
  } catch (e) {
    console.error("No se pudo parsear JSON de /car-models:", e);
    carModels = [];
  }

  if (!Array.isArray(carModels) || carModels.length === 0) {
    throw new Error(
      "No hay car-models en la BD PERF. Revisá seed_perf o seed_demo."
    );
  }

  const selectedModels = carModels.slice(0, N_MODELS);

  // 3) Crear items de inventario para esos car_models
  const inventoryItems = [];

  for (const cm of selectedModels) {
    const payload = JSON.stringify({
      car_model_id: cm.id,
      brand: cm.brand,
      model: cm.model,
      quantity: INVENTORY_QTY, // ej. 2200 unidades reales en inventario
    });

    const invRes = http.post(`${BASE_URL}/inventory`, payload, {
      headers: agencyHeaders,
    });

    check(invRes, {
      "inventario creado 201": (r) => r.status === 201,
    });

    try {
      const invBody = invRes.json();
      if (invBody && invBody.id) {
        inventoryItems.push(invBody);
      }
    } catch (e) {
      console.error("No se pudo parsear JSON de creación de inventario:", e);
    }
  }

  if (inventoryItems.length === 0) {
    throw new Error(
      "No se pudieron crear items de inventario para el test de perf."
    );
  }

  // 4) Crear listings/ofertas para esos items de inventario
  const listingIds = [];

  for (const inv of inventoryItems) {
    const payload = JSON.stringify({
      inventory_id: inv.id,
      current_price_amount: 12000,
      current_price_currency: "USD",
      brand: inv.brand,
      model: inv.model,
      // stock de la oferta: un poco menor que INVENTORY_QTY
      stock: Math.min(inv.quantity ?? INVENTORY_QTY, LISTING_STOCK),
      seller_notes: "PERF_K6_STRESS_PURCHASES",
    });

    const listRes = http.post(`${BASE_URL}/listings`, payload, {
      headers: agencyHeaders,
    });

    check(listRes, {
      "listing creado 201": (r) => r.status === 201,
    });

    try {
      const body = listRes.json();
      if (body && body.id) {
        listingIds.push(body.id);
      }
    } catch (e) {
      console.error("No se pudo parsear JSON de creación de listing:", e);
    }
  }

  if (listingIds.length === 0) {
    throw new Error(
      "No se pudieron crear listings para el test de stress de compras."
    );
  }

  console.log(
    `Listings creados para stress de compras: ${listingIds.join(", ")}`
  );

  // Devolvemos datos para default():
  // - ids de listings creados
  // - token del buyer (para hacer /purchases)
  return { listingIds, buyerToken };
}

// ----------------------------------------------------------
// default(data): ejecutado por cada VU en cada iteración.
// - Toma un listing_id de los creados en setup().
// - Hace POST /purchases con quantity=1 usando buyerToken.
// ----------------------------------------------------------
export default function (data) {
  const listingIds = data.listingIds || [];
  const buyerToken = data.buyerToken;

  if (!buyerToken) {
    console.error(
      "buyerToken no disponible en data. Revisá el setup() de stress-purchases.js."
    );
    return;
  }

  if (!listingIds.length) {
    console.error(
      "No hay listingIds en data. Revisá el setup() de stress-purchases.js."
    );
    return;
  }

  const listingId = listingIds[Math.floor(Math.random() * listingIds.length)];

  const url = `${BASE_URL}/purchases`;
  const payload = JSON.stringify({
    listing_id: listingId,
    quantity: 1,
  });

  const headers = {
    Authorization: `Bearer ${buyerToken}`,
    "Content-Type": "application/json",
  };

  const res = http.post(url, payload, { headers });

  check(res, {
    // La mayoría deberían ser 201, pero aceptamos que algunas sean 400 por stock agotado
    "compra exitosa (201) o rechazada por stock (400)": (r) =>
      r.status === 201 ||
      (r.status === 400 &&
        (r.json("detail") ?? "").toString().toLowerCase().includes("stock")),
    "respuesta es JSON": (r) =>
      r.headers["Content-Type"]?.includes("application/json"),
  });

  sleep(0.5);
}
