import enum
from sqlalchemy import (
    Integer,
    String,
    Enum,
    Boolean,
    DateTime,
    ForeignKey,
    func,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    buyer = "buyer"
    agency = "agency"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    agency_id: Mapped[int | None] = mapped_column(
        ForeignKey("agencies.id"), nullable=True
    )
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    agency = relationship("Agency", lazy="joined")

    favorites = relationship(
        "Favorite", back_populates="customer", cascade="all, delete-orphan"
    )

    purchases = relationship(
        "Purchase", back_populates="buyer", cascade="all, delete-orphan"
    )

    reviews = relationship(
        "Review", back_populates="author", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # Para role='agency' obliga un único usuario por agency_id.
        # (MySQL permite múltiples NULL; admin/buyer llevan agency_id NULL)
        UniqueConstraint("agency_id", "role", name="uq_user_agency_role"),
    )

    # 👇 clave: usar 'role' como discriminador de la jerarquía
    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": None,  # base abstracta
    }


# --- Subclases concretas (mismo 'users' table) ---
class Admin(User):
    __mapper_args__ = {"polymorphic_identity": UserRole.admin}

    # ejemplo de comportamiento propio (servicio adentro)
    def top_cars(self, db, top: int = 5):
        # placeholder: acá llamarías a repos/reportes reales
        return []


class Customer(User):
    __mapper_args__ = {"polymorphic_identity": UserRole.buyer}

    def add_favourite(self, db, listing_id: int):
        # placeholder de regla de negocio
        pass


class AgencyUser(User):
    __mapper_args__ = {"polymorphic_identity": UserRole.agency}

    def post_offer(self, db, data):
        # placeholder para publicar oferta
        pass
