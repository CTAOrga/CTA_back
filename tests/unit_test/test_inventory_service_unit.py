import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.car_model import CarModel
from app.models.inventory import Inventory
from app.models.agency import Agency
from app.services.inventory import (
    create_inventory_item,
    list_inventory_items,
    get_inventory_item_for_agency,
    update_inventory_item,
    delete_inventory_item,
)


def test_create_inventory_item_creates_and_consolidates(
    db: Session,
    agency: Agency,
) -> None:
    """
    create_inventory_item:
      - Primera vez crea un registro de inventario.
      - Segunda vez, con mismo (agency_id, brand, model), NO crea otro,
        sino que consolida la cantidad (suma).
    """

    # Definimos el modelo de auto en el catálogo
    car_model = CarModel(
        brand="Fiat",
        model="Cronos",
    )
    db.add(car_model)
    db.commit()
    db.refresh(car_model)

    # 1) Primera carga de inventario
    inv1 = create_inventory_item(
        db=db,
        agency_id=agency.id,
        brand="Fiat",
        model="Cronos",
        quantity=3,
    )

    assert isinstance(inv1, Inventory)
    assert inv1.agency_id == agency.id
    assert inv1.car_model_id == car_model.id
    assert inv1.quantity == 3

    # 2) Segunda carga para el mismo modelo / agencia
    inv2 = create_inventory_item(
        db=db,
        agency_id=agency.id,
        brand="Fiat",
        model="Cronos",
        quantity=2,
    )

    # Debe ser el MISMO registro, con cantidad consolidada
    assert inv2.id == inv1.id
    assert inv2.quantity == 5  # 3 + 2


def test_list_inventory_items_paginates_and_filters(
    db: Session,
    agency: Agency,
) -> None:
    """
    list_inventory_items:
      - Devuelve un payload con items + total + page + page_size.
      - Permite filtrar por brand/model.
    """

    # Creamos modelos en el catálogo
    c1 = CarModel(brand="Fiat", model="Cronos")
    c2 = CarModel(brand="Toyota", model="Yaris")
    c3 = CarModel(brand="Ford", model="Fiesta")

    db.add_all([c1, c2, c3])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)
    db.refresh(c3)

    # Creamos inventario para la misma agencia
    inv1 = Inventory(agency_id=agency.id, car_model_id=c1.id, quantity=10)
    inv2 = Inventory(agency_id=agency.id, car_model_id=c2.id, quantity=5)
    inv3 = Inventory(agency_id=agency.id, car_model_id=c3.id, quantity=1)
    db.add_all([inv1, inv2, inv3])
    db.commit()

    # 1) Sin filtros, página 1, page_size grande
    result = list_inventory_items(
        db=db,
        agency_id=agency.id,
        page=1,
        page_size=10,
        brand=None,
        model=None,
    )

    assert isinstance(result, dict)
    assert set(result.keys()) == {"items", "total", "page", "page_size"}
    assert result["total"] == 3
    assert result["page"] == 1
    assert result["page_size"] == 10
    assert len(result["items"]) == 3

    # 2) Filtro por brand = "Fiat"
    result_fiat = list_inventory_items(
        db=db,
        agency_id=agency.id,
        page=1,
        page_size=10,
        brand="Fiat",
        model=None,
    )

    assert result_fiat["total"] == 1
    assert len(result_fiat["items"]) == 1
    item = result_fiat["items"][0]
    assert item["brand"] == "Fiat"
    assert item["model"] == "Cronos"
    assert item["quantity"] == 10

    # 3) Filtro por model = "Yaris"
    result_yaris = list_inventory_items(
        db=db,
        agency_id=agency.id,
        page=1,
        page_size=10,
        brand=None,
        model="Yaris",
    )

    assert result_yaris["total"] == 1
    assert len(result_yaris["items"]) == 1
    item2 = result_yaris["items"][0]
    assert item2["brand"] == "Toyota"
    assert item2["model"] == "Yaris"
    assert item2["quantity"] == 5


def test_update_and_delete_inventory_item(
    db: Session,
    agency: Agency,
) -> None:
    """
    update_inventory_item y delete_inventory_item:
      - update cambia la cantidad para un item de la agencia.
      - delete lo elimina y luego no puede volver a obtenerse.
    """

    # Preparamos catálogo + inventario inicial
    car_model = CarModel(brand="Peugeot", model="208")
    db.add(car_model)
    db.commit()
    db.refresh(car_model)

    inv = Inventory(
        agency_id=agency.id,
        car_model_id=car_model.id,
        quantity=7,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # 1) update_inventory_item: cambiamos cantidad a 15
    updated = update_inventory_item(
        db=db,
        inventory_id=inv.id,
        agency_id=agency.id,
        quantity=15,
    )

    assert updated.id == inv.id
    assert updated.quantity == 15

    # 2) delete_inventory_item: lo eliminamos
    delete_inventory_item(
        db=db,
        inventory_id=inv.id,
        agency_id=agency.id,
    )

    # Ya no debería poder obtenerse para esta agencia
    with pytest.raises(HTTPException) as excinfo:
        get_inventory_item_for_agency(
            db=db,
            inventory_id=inv.id,
            agency_id=agency.id,
        )

    assert excinfo.value.status_code == 404
