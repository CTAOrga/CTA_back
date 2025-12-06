from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session
import pytest

from app.models.user import User
from app.models.listing import Listing

PURCHASE_PATH = "/api/v1/purchases"
ADMIN_REPORTS_TOP_SOLD_CARS_PATH = "/api/v1/admin/reports/top-sold-cars"


def _login(client: TestClient, email: str, password: str = "secret") -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    return resp.json()["access_token"]


def test_admin_top_sold_cars_report_with_excluded_sold_cars(
    client: TestClient,
    db: Session,
    admin_user: User,
    buyer_user: User,
    listings_for_top_selling: list[Listing],
):
    """
    Escenario de integración:

    Tenemos 7 autos distintos (listings_for_top_selling) y el buyer compra:

        index 0 -> 6 unidades
        index 1 -> 5
        index 2 -> 4
        index 3 -> 3
        index 4 -> 2
        index 5 -> 1
        index 6 -> 1

    El reporte de Top 5 debe incluir solo los 5 más vendidos (6,5,4,3,2),
    dejando AFUERA a los autos con 1 unidad vendida, aunque tengan ventas.
    """

    # 1) Login buyer
    buyer_token = _login(client, buyer_user.email)

    # 2) Plan de compras: 6,5,4,3,2,1,1
    purchase_plan = [6, 5, 4, 3, 2, 1, 1]
    assert len(purchase_plan) == len(listings_for_top_selling)

    for listing, times in zip(listings_for_top_selling, purchase_plan):
        for _ in range(times):
            resp = client.post(
                PURCHASE_PATH,
                json={"listing_id": listing.id, "quantity": 1},
                headers={"Authorization": f"Bearer {buyer_token}"},
            )
            assert resp.status_code == status.HTTP_201_CREATED, resp.text

    # 3) Login admin
    admin_token = _login(client, admin_user.email)

    # 4) Admin consulta el reporte de autos más vendidos (Top 5 por defecto)
    resp_report = client.get(
        ADMIN_REPORTS_TOP_SOLD_CARS_PATH,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_report.status_code == status.HTTP_200_OK, resp_report.text

    report_data = resp_report.json()
    assert isinstance(report_data, list)

    # Debe devolver exactamente 5 filas (Top 5)
    assert len(report_data) == 5

    # 5) Construimos lo esperado (todas las ventas, incluidas las que quedarán fuera)
    expected_units = {}
    expected_amounts = {}
    for listing, count in zip(listings_for_top_selling, purchase_plan):
        key = (listing.brand, listing.model)
        expected_units[key] = count
        expected_amounts[key] = float(listing.current_price_amount) * count

    # 6) Verificamos que el reporte esté ordenado por units_sold desc
    units_sold_list = []
    reported_keys = set()

    for row in report_data:
        brand = row["brand"]
        model = row["model"]
        units_sold = row["units_sold"]
        total_amount = row["total_amount"]

        key = (brand, model)
        reported_keys.add(key)

        # Cada auto reportado tiene que estar en el conjunto esperado
        assert key in expected_units, f"Auto inesperado en el reporte: {key}"

        # Unidades vendidas correctas para ese auto
        assert units_sold == expected_units[key], (
            f"units_sold incorrecto para {key}: "
            f"{units_sold} != {expected_units[key]}"
        )

        # Monto total correcto
        assert total_amount == pytest.approx(expected_amounts[key]), (
            f"total_amount incorrecto para {key}: "
            f"{total_amount} != {expected_amounts[key]}"
        )

        units_sold_list.append(units_sold)

    # El listado debe venir ordenado de mayor a menor por units_sold
    assert units_sold_list == sorted(units_sold_list, reverse=True)

    # 7) El top5 debe ser exactamente las cantidades [6,5,4,3,2]
    assert units_sold_list == [6, 5, 4, 3, 2]

    # 8) Los autos con 1 unidad vendida deben QUEDAR AFUERA del top5
    listing_5 = listings_for_top_selling[5]  # ventas = 1
    listing_6 = listings_for_top_selling[6]  # ventas = 1

    key_5 = (listing_5.brand, listing_5.model)
    key_6 = (listing_6.brand, listing_6.model)

    assert key_5 not in reported_keys
    assert key_6 not in reported_keys
