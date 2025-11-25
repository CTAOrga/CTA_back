from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional, Literal

from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.models.listing import Listing
from app.schemas.listing import (
    ListingCreate,
    ListingOut,
    ListingUpdate,
)
from app.api.deps import optional_current_user, get_current_user
from app.models.favorite import Favorite
from app.services import listings as listings_service
from app.models.review import Review
from app.services import inventory as inventory_service

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=list[ListingOut])
def list_listings(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Búsqueda por marca o modelo"),
    brand: Optional[str] = None,
    model: Optional[str] = None,
    agency_id: Optional[str] = Query(None),
    min_price: Optional[str] = Query(None),
    max_price: Optional[str] = Query(None),
    sort: Optional[Literal["price_asc", "price_desc", "newest"]] = "newest",
    page: int = 1,
    page_size: int = 20,
    current_user: Optional[User] = Depends(optional_current_user),
):
    query = db.query(Listing)

    def to_int(v):
        return None if v in (None, "", "null", "undefined") else int(v)

    def to_float(v):
        return None if v in (None, "", "null", "undefined") else float(v)

    # Filtros
    aid = to_int(agency_id)
    if aid is not None:
        query = query.filter(Listing.agency_id == aid)

    mi = to_float(min_price)
    if mi is not None:
        query = query.filter(Listing.current_price_amount >= mi)

    ma = to_float(max_price)
    if ma is not None:
        query = query.filter(Listing.current_price_amount <= ma)

    if q:
        like = f"%{q}%"
        query = query.filter((Listing.brand.ilike(like)) | (Listing.model.ilike(like)))

    if brand:
        query = query.filter(Listing.brand == brand)
    if model:
        query = query.filter(Listing.model == model)

    # Orden
    if sort == "price_asc":
        query = query.order_by(Listing.current_price_amount.asc())
    elif sort == "price_desc":
        query = query.order_by(Listing.current_price_amount.desc())
    else:
        query = query.order_by(Listing.id.desc())

    # Paginación
    page = max(page, 1)
    offset = (page - 1) * page_size
    items: list[Listing] = query.offset(offset).limit(page_size).all()

    # Favoritos (si hay user buyer)
    fav_ids: set[int] = set()
    if current_user and current_user.role == UserRole.buyer and items:
        ids = [it.id for it in items]
        rows = (
            db.query(Favorite.listing_id)
            .filter(
                Favorite.customer_id == current_user.id,
                Favorite.listing_id.in_(ids),
            )
            .all()
        )
        fav_ids = {rid for (rid,) in rows}

    # 👇 NUEVO: agregados de ratings por car_model
    car_model_ids = {it.car_model_id for it in items if it.car_model_id is not None}

    ratings_map: dict[int, tuple[float, int]] = {}
    if car_model_ids:
        agg_rows = (
            db.query(
                Review.car_model_id,
                func.avg(Review.rating).label("avg_rating"),
                func.count(Review.id).label("count_reviews"),
            )
            .filter(Review.car_model_id.in_(car_model_ids))
            .group_by(Review.car_model_id)
            .all()
        )
        ratings_map = {
            cm_id: (float(avg_rating), int(count_reviews))
            for (cm_id, avg_rating, count_reviews) in agg_rows
        }

    result: list[ListingOut] = []

    for it in items:
        base = ListingOut.model_validate(it, from_attributes=True)
        is_favorite = it.id in fav_ids

        avg_rating = None
        reviews_count = 0
        if it.car_model_id and it.car_model_id in ratings_map:
            avg_rating, reviews_count = ratings_map[it.car_model_id]

        result.append(
            base.model_copy(
                update={
                    "is_favorite": is_favorite,
                    "avg_rating": avg_rating,
                    "reviews_count": reviews_count,
                }
            )
        )

    return result


@router.post(
    "",
    response_model=ListingOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.agency))],
)
def create_listing(
    payload: ListingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Si el payload trae agency_id, validamos que coincida con la agencia del user
    if user.agency_id is None:
        raise HTTPException(400, "El usuario de agencia no tiene agency_id asignado")
    # if payload.agency_id != user.agency_id:
    #    raise HTTPException(403, "No podés crear ofertas para otra agencia")

    try:
        inv = inventory_service.get_inventory_item_for_agency(
            db=db,
            inventory_id=payload.inventory_id,
            agency_id=user.agency_id,
        )
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Item de inventario no encontrado para esta agencia",
        )

    car_model = inv.car_model  # relación desde AgencyInventory

    listing = Listing(
        agency_id=user.agency_id,
        car_model_id=car_model.id,
        brand=car_model.brand,
        model=car_model.model,
        current_price_amount=payload.current_price_amount,
        current_price_currency=payload.current_price_currency,
        stock=payload.stock,
        seller_notes=payload.seller_notes,
        expires_on=payload.expires_on,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.patch(
    "/{listing_id}",
    response_model=ListingOut,
    dependencies=[Depends(require_role(UserRole.agency))],
)
def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(404, "Listing no encontrada")
    if user.agency_id != listing.agency_id:
        raise HTTPException(403, "No podés modificar ofertas de otra agencia")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(listing, k, v)

    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("agency")),
):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(404, "Listing no encontrada")
    if user.agency_id != listing.agency_id:
        raise HTTPException(403, "No podés borrar ofertas de otra agencia")

    db.delete(listing)
    db.commit()
    return None


@router.get(
    "/{listing_id}",
    response_model=ListingOut,
    dependencies=[Depends(require_role(UserRole.buyer))],
)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve el detalle de una oferta para un comprador logueado,
    incluyendo si está marcada como favorita.
    """
    logger.info(f"[endpoint] listing_id={listing_id}, current_user={current_user!r}")
    return listings_service.get_listing_for_buyer(
        db=db,
        buyer=current_user,
        listing_id=listing_id,
    )


@router.post(
    "/{listing_id}/cancel",
    dependencies=[Depends(require_role(UserRole.agency))],
)
def cancel_my_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agency_id = current_user.agency_id
    if not agency_id:
        raise HTTPException(
            status_code=400,
            detail="Usuario sin agencia asociada",
        )

    return listings_service.cancel_listing(db, listing_id, agency_id)


@router.post(
    "/{listing_id}/activate",
    dependencies=[Depends(require_role(UserRole.agency))],
)
def activate_my_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agency_id = current_user.agency_id
    if not agency_id:
        raise HTTPException(
            status_code=400,
            detail="Usuario sin agencia asociada",
        )

    return listings_service.activate_listing(db, listing_id, agency_id)


@router.delete(
    "/{listing_id}",
    status_code=204,
    dependencies=[Depends(require_role(UserRole.agency))],
)
def delete_my_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agency_id = current_user.agency_id
    if not agency_id:
        raise HTTPException(
            status_code=400,
            detail="Usuario sin agencia asociada",
        )

    listings_service.delete_listing(db, listing_id, agency_id)
    return None
