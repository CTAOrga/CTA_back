from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole, Customer
from app.schemas.user import RegisterBuyer, LoginInput, TokenOut, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user
from app.services.auth_service import authenticate

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_buyer(payload: RegisterBuyer, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = Customer(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.buyer,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(payload: LoginInput, db: Session = Depends(get_db)):
    user = authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    token = create_access_token(
        sub=str(user.id),
        role=user.role.value,  # si tu create_access_token espera string
        agency_id=user.agency_id,
    )
    return {
        "access_token": token,
        "role": user.role,  # si tu TokenOut acepta Enum, dejalo así; si no, usa user.role.value
        "agency_id": user.agency_id,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current
