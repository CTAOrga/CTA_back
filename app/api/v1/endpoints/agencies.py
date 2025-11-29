from datetime import date
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.api.deps import require_role
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole, AgencyUser
from app.models.agency import Agency
from app.schemas.purchase import AgencyCustomerOut, AgencySaleOut
from app.schemas.user import CreateAgencyUser, UserOut
from app.schemas.listing import ListingOut, PaginatedListingsOut
from app.services import listings as listings_service
from app.services import purchases as purchases_service
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemOut,
    PaginatedInventoryOut,
)
from app.services import inventory as inventory_service

router = APIRouter()


@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.admin))],
)
def create_agency_user(payload: CreateAgencyUser, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    agency = db.query(Agency).filter(Agency.name == payload.agency_name).first()
    if not agency:
        agency = Agency(name=payload.agency_name)
        db.add(agency)
        db.flush()  # toma agency.id sin cerrar transacción

    user = AgencyUser(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.agency,
        agency_id=agency.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get(
    "/my-listings",
    response_model=PaginatedListingsOut,
    dependencies=[Depends(require_role(UserRole.agency))],
)
def my_listings(
    page: int = 1,
    page_size: int = 10,
    brand: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort: Optional[Literal["price_asc", "price_desc", "newest"]] = "newest",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve los listings de la agencia logueada, paginados.
    """
    agency_id = current_user.agency_id

    if agency_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario de agencia no tiene una agencia asociada",
        )

    return listings_service.list_my_agency_listings(
        db=db,
        agency_id=agency_id,
        page=page,
        page_size=page_size,
        brand=brand,
        model=model,
        is_active=is_active,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
    )


@router.get(
    "/my-listings/{listing_id}",
    response_model=ListingOut,
    dependencies=[Depends(require_role(UserRole.agency))],
)
def get_my_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return listings_service.get_listing_owned_by_agency(
        db, listing_id, current_user.agency_id
    )


@router.get(
    "/my-sales",
    response_model=list[AgencySaleOut],
    dependencies=[Depends(require_role(UserRole.agency))],
)
def my_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    brand: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    customer: Optional[str] = Query(None, description="Nombre o email del cliente"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
):
    """
    Devuelve las ventas de la agencia logueada, con filtros opcionales.
    """
    if current_user.agency_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario de agencia no tiene una agencia asociada",
        )

    return purchases_service.list_sales_for_agency(
        db=db,
        agency_id=current_user.agency_id,
        brand=brand,
        model=model,
        customer=customer,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/my-customers",
    response_model=list[AgencyCustomerOut],
    dependencies=[Depends(require_role(UserRole.agency))],
)
def my_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    q: Optional[str] = Query(None, description="Nombre o email del cliente"),
    min_purchases: Optional[int] = Query(None, ge=1),
    min_spent: Optional[float] = Query(None, ge=0.0),
):
    """
    Devuelve el resumen de clientes con filtros opcionales.
    """
    if current_user.agency_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario de agencia no tiene una agencia asociada",
        )

    return purchases_service.list_customers_for_agency(
        db=db,
        agency_id=current_user.agency_id,
        q=q,
        min_purchases=min_purchases,
        min_spent=min_spent,
    )


@router.get(
    "/my-inventory",
    response_model=PaginatedInventoryOut,
    dependencies=[Depends(require_role(UserRole.agency))],
)
def my_inventory(
    page: int = 1,
    page_size: int = 20,
    brand: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    is_used: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.agency_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario de agencia no tiene una agencia asociada",
        )

    data = inventory_service.list_inventory_items(
        db=db,
        agency_id=current_user.agency_id,
        page=page,
        page_size=page_size,
        brand=brand,
        model=model,
        is_used=is_used,
    )

    items = [
        InventoryItemOut(
            id=it["id"],
            car_model_id=it["car_model_id"],
            brand=it["brand"],
            model=it["model"],
            quantity=it["quantity"],
            is_used=it["is_used"],
        )
        for it in data["items"]
    ]

    return PaginatedInventoryOut(
        items=items,
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
    )


@router.post(
    "/my-inventory",
    response_model=InventoryItemOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.agency))],
)
def create_inventory(
    payload: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.agency_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario de agencia no tiene una agencia asociada",
        )

    inv = inventory_service.create_inventory_item(
        db=db,
        agency_id=current_user.agency_id,
        brand=payload.brand,
        model=payload.model,
        quantity=payload.quantity,
        is_used=payload.is_used,
    )

    return InventoryItemOut(
        id=inv.id,
        car_model_id=inv.car_model_id,
        brand=inv.car_model.brand,
        model=inv.car_model.model,
        quantity=inv.quantity,
        is_used=inv.is_used,
    )


@router.patch(
    "/my-inventory/{inventory_id}",
    response_model=InventoryItemOut,
    dependencies=[Depends(require_role(UserRole.agency))],
)
def update_inventory(
    inventory_id: int,
    payload: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.agency_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario de agencia no tiene una agencia asociada",
        )

    try:
        inv = inventory_service.update_inventory_item(
            db=db,
            inventory_id=inventory_id,
            agency_id=current_user.agency_id,
            quantity=payload.quantity,
            is_used=payload.is_used,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")

    return InventoryItemOut(
        id=inv.id,
        car_model_id=inv.car_model_id,
        brand=inv.car_model.brand,
        model=inv.car_model.model,
        quantity=inv.quantity,
        is_used=inv.is_used,
    )
