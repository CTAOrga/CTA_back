from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole, AgencyUser
from app.models.agency import Agency
from app.schemas.user import CreateAgencyUser, UserOut

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
