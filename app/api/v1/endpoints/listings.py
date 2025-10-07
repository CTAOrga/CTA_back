from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, Literal

from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.models.listing import Listing
from app.schemas.listing import ListingOut, ListingCreate, ListingUpdate
from app.api.deps import optional_current_user
from app.models.favorite import Favorite


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
    if agency_id:
        query = query.filter(Listing.agency_id == agency_id)
    if min_price is not None:
        query = query.filter(Listing.current_price_amount >= min_price)
    if max_price is not None:
        query = query.filter(Listing.current_price_amount <= max_price)

    if sort == "price_asc":
        query = query.order_by(Listing.current_price_amount.asc())
    elif sort == "price_desc":
        query = query.order_by(Listing.current_price_amount.desc())
    else:
        query = query.order_by(Listing.id.desc())

    page = max(page, 1)
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    fav_ids: set[int] = set()
    if current_user and current_user.role == UserRole.buyer and items:
        ids = [it.id for it in items]
        rows = (
            db.query(Favorite.listing_id)
            .filter(
                Favorite.customer_id == current_user.id, Favorite.listing_id.in_(ids)
            )
            .all()
        )
        fav_ids = {rid for (rid,) in rows}

    return [
        ListingOut.model_validate(it, from_attributes=True).model_copy(
            update={"is_favorite": it.id in fav_ids}
        )
        for it in items
    ]


@router.post("", response_model=ListingOut, status_code=status.HTTP_201_CREATED)
def create_listing(
    payload: ListingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.agency)),
):
    # Si el payload trae agency_id, validamos que coincida con la agencia del user
    if user.agency_id is None:
        raise HTTPException(400, "El usuario de agencia no tiene agency_id asignado")
    if payload.agency_id != user.agency_id:
        raise HTTPException(403, "No podés crear ofertas para otra agencia")

    listing = Listing(
        agency_id=payload.agency_id,
        brand=payload.brand,
        model=payload.model,
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


@router.patch("/{listing_id}", response_model=ListingOut)
def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("agency")),
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
