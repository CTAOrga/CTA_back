from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session
from fastapi import status

from app.models.purchase import Purchase
from app.models.listing import Listing
from app.models.user import User

PURCHASE_PATH = "/api/v1/purchases"
AGENCY_CUSTOMERS_PATH = "/api/v1/agencies/my-customers"
ADMIN_PURCHASES_PATH = "/api/v1/admin/purchases"
ADMIN_REPORTS_BUYERS_PATH = "api/v1/admin/reports/top-buyers"


def _login(client: TestClient, email: str, password: str = "secret") -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    return resp.json()["access_token"]


def test_buyer_purchases_listing_and_agency_sees_customer(
    client: TestClient,
    db: Session,
    buyer_user: User,
    agency_user: User,
    admin_user: User,
    sample_listing: Listing,
):
    # Login del buyer para obtener token
    buyer_token = _login(client, buyer_user.email)

    # Guardamos stock inicial
    db.refresh(sample_listing)
    initial_stock = sample_listing.stock

    # Buyer realiza la compra
    resp = client.post(
        PURCHASE_PATH,
        json={"listing_id": sample_listing.id, "quantity": 1},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    purchase_body = resp.json()
    assert purchase_body["listing_id"] == sample_listing.id
    assert purchase_body["buyer_id"] == buyer_user.id
    assert purchase_body["quantity"] == 1

    # Verificamos en DB que la Purchase exista
    purchase_in_db = (
        db.query(Purchase)
        .filter(
            Purchase.id == purchase_body["id"],
            Purchase.listing_id == sample_listing.id,
            Purchase.buyer_id == buyer_user.id,
        )
        .first()
    )
    assert purchase_in_db is not None

    # Stock disminuyó en 1
    db.refresh(sample_listing)
    assert sample_listing.stock == initial_stock - 1

    # Login agency para consultar sus clientes/ventas
    agency_token = _login(client, agency_user.email)

    # Agency consulta sus clientes
    resp_customers = client.get(
        AGENCY_CUSTOMERS_PATH,
        headers={"Authorization": f"Bearer {agency_token}"},
    )
    assert resp_customers.status_code == status.HTTP_200_OK, resp_customers.text
    customers = resp_customers.json()

    customers_ids = {c["customer_id"] for c in customers}
    assert buyer_user.id in customers_ids
    customers_emails = {c["email"] for c in customers}
    assert buyer_user.email in customers_emails

    admin_token = _login(client, admin_user.email)

    # Admin ve la compra en el listado global de compras
    resp_admin_purchases = client.get(
        ADMIN_PURCHASES_PATH,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert (
        resp_admin_purchases.status_code == status.HTTP_200_OK
    ), resp_admin_purchases.text
    admin_data_purchases = resp_admin_purchases.json()

    admin_purchases = admin_data_purchases.get("items", [])

    found_purchase = any(
        p["id"] == purchase_body["id"]
        and p["listing_id"] == sample_listing.id
        and p["buyer_id"] == buyer_user.id
        for p in admin_purchases
    )
    assert found_purchase, "Admin no ve la compra del buyer en el listado de compras"

    # Admin ve al buyer en el reporte de usuarios con más compras (Top buyers)
    resp_top_buyers = client.get(
        ADMIN_REPORTS_BUYERS_PATH,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_top_buyers.status_code == status.HTTP_200_OK, resp_top_buyers.text
    top_buyers = resp_top_buyers.json()

    # Debe ser una lista
    assert isinstance(top_buyers, list)

    # Buscamos la entrada correspondiente al buyer de la prueba
    buyer_entry = next(
        (b for b in top_buyers if b["buyer_id"] == buyer_user.id),
        None,
    )
    assert (
        buyer_entry is not None
    ), "Admin no ve al buyer en el reporte de top compradores"

    assert buyer_entry["email"] == buyer_user.email
    assert buyer_entry["purchases_count"] >= 1

    assert buyer_entry["total_spent"] == pytest.approx(
        float(sample_listing.current_price_amount)
    )
