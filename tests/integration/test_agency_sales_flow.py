from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.listing import Listing
from app.models.purchase import Purchase
from app.models.inventory import Inventory
from app.models.car_model import CarModel
from app.models.agency import Agency

PURCHASE_PATH = "/api/v1/purchases"
AGENCY_CUSTOMERS_PATH = "/api/v1/agencies/my-customers"
AGENCY_SALES_PATH = "/api/v1/agencies/my-sales"
LISTINGS_PATH = "/api/v1/listings"


def _login(client: TestClient, email: str, password: str = "secret") -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    return resp.json()["access_token"]


def test_agency_creates_listing_and_sees_clients_and_sales(
    client: TestClient,
    db: Session,
    agency: Agency,
    agency_user: User,
    buyer_user: User,
    second_buyer_user: User,
    fiat_cronos_carmodel: CarModel,
    fiat_cronos_inventory: Inventory,
):
    """
    Flujo integración Concesionaria:

    - Agency crea un listing (oferta) sobre un inventory existente.
    - Dos buyers compran esa oferta.
    - La agency los ve como clientes en /my-customers.
    - En la DB se ven las ventas (Purchases) asociadas a su listing.
    """

    # 1) Login agency
    agency_token = _login(client, agency_user.email)

    # 2) Agency crea un listing vía API
    listing_payload = {
        "brand": "Fiat",
        "model": "Cronos",
        "inventory_id": fiat_cronos_inventory.id,
        "current_price_amount": 12000.0,
        "current_price_currency": "USD",
        "stock": 5,
        "seller_notes": "Oferta integración agency",
    }
    resp_listing = client.post(
        LISTINGS_PATH,
        json=listing_payload,
        headers={"Authorization": f"Bearer {agency_token}"},
    )
    assert resp_listing.status_code == status.HTTP_201_CREATED, resp_listing.text
    listing_body = resp_listing.json()
    listing_id = listing_body["id"]

    # Verificamos en DB que el listing esté bien asociado
    listing_db: Listing | None = db.query(Listing).get(listing_id)
    assert listing_db is not None
    assert listing_db.agency_id == agency.id
    assert listing_db.car_model_id == fiat_cronos_carmodel.id

    # 3) Dos buyers compran el listing
    buyer1_token = _login(client, buyer_user.email)
    buyer2_token = _login(client, second_buyer_user.email)

    # Buyer 1 compra 1 unidad
    resp_purchase_1 = client.post(
        PURCHASE_PATH,
        json={"listing_id": listing_id, "quantity": 1},
        headers={"Authorization": f"Bearer {buyer1_token}"},
    )
    assert resp_purchase_1.status_code == status.HTTP_201_CREATED, resp_purchase_1.text
    p1_body = resp_purchase_1.json()

    # Buyer 2 compra 2 unidades
    resp_purchase_2 = client.post(
        PURCHASE_PATH,
        json={"listing_id": listing_id, "quantity": 2},
        headers={"Authorization": f"Bearer {buyer2_token}"},
    )
    assert resp_purchase_2.status_code == status.HTTP_201_CREATED, resp_purchase_2.text
    p2_body = resp_purchase_2.json()

    # Verificamos las purchases en DB
    p1_db = (
        db.query(Purchase)
        .filter(
            Purchase.id == p1_body["id"],
            Purchase.listing_id == listing_id,
            Purchase.buyer_id == buyer_user.id,
        )
        .first()
    )
    p2_db = (
        db.query(Purchase)
        .filter(
            Purchase.id == p2_body["id"],
            Purchase.listing_id == listing_id,
            Purchase.buyer_id == second_buyer_user.id,
        )
        .first()
    )
    assert p1_db is not None
    assert p2_db is not None

    # 4) La agency ve a esos buyers como clientes en /my-customers
    resp_customers = client.get(
        AGENCY_CUSTOMERS_PATH,
        headers={"Authorization": f"Bearer {agency_token}"},
    )
    assert resp_customers.status_code == status.HTTP_200_OK, resp_customers.text
    customers = resp_customers.json()

    assert isinstance(customers, list)

    # DTO: AgencyCustomerOut
    # customer_id, email, total_purchases, total_spent, last_purchase_at

    buyer1_customer = next(
        (c for c in customers if c["customer_id"] == buyer_user.id),
        None,
    )
    buyer2_customer = next(
        (c for c in customers if c["customer_id"] == second_buyer_user.id),
        None,
    )

    assert buyer1_customer is not None, "Buyer 1 no aparece como cliente de la agency"
    assert buyer2_customer is not None, "Buyer 2 no aparece como cliente de la agency"

    assert buyer1_customer["email"] == buyer_user.email
    assert buyer2_customer["email"] == second_buyer_user.email

    # Sólo chequeamos que la agregación sea coherente
    assert buyer1_customer["total_purchases"] >= 1
    assert buyer2_customer["total_purchases"] >= 1

    assert buyer1_customer["total_spent"] > 0.0
    assert buyer2_customer["total_spent"] > 0.0

    assert buyer1_customer["last_purchase_at"] is not None
    assert buyer2_customer["last_purchase_at"] is not None

    # 5) La agency ve las ventas en /my-sales
    resp_sales = client.get(
        AGENCY_SALES_PATH,
        headers={"Authorization": f"Bearer {agency_token}"},
    )
    assert resp_sales.status_code == status.HTTP_200_OK, resp_sales.text
    sales = resp_sales.json()

    assert isinstance(sales, list)

    # Filtramos sólo las ventas del listing creado en este test
    sales_for_listing = [s for s in sales if s.get("listing_id") == listing_id]
    assert (
        len(sales_for_listing) >= 2
    ), "La agency debería ver al menos 2 ventas para ese listing"

    # Chequeamos que haya una venta de cada buyer
    has_sale_buyer1 = any(s.get("buyer_id") == buyer_user.id for s in sales_for_listing)
    has_sale_buyer2 = any(
        s.get("buyer_id") == second_buyer_user.id for s in sales_for_listing
    )

    assert has_sale_buyer1, "No se encontró venta para Buyer 1 en /my-sales"
    assert has_sale_buyer2, "No se encontró venta para Buyer 2 en /my-sales"

    # Si AgencySaleOut tiene 'quantity', chequeamos que la suma total sea coherente
    total_quantity = sum(s.get("quantity", 0) for s in sales_for_listing)
    assert total_quantity >= 3  # 1 + 2 en este flujo
