from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.api.deps import require_role
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole, AgencyUser
from app.models.agency import Agency
from app.schemas.user import CreateAgencyUser, UserOut
from app.schemas.listing import ListingOut, PaginatedListingsOut
from app.services import listings as listings_service

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
