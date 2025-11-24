from decimal import Decimal
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Numeric,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.car_model import CarModel


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agency_id: Mapped[int] = mapped_column(
        ForeignKey("agencies.id", ondelete="CASCADE"), index=True
    )

    car_model_id: Mapped[int] = mapped_column(
        ForeignKey("car_models.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    brand: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    current_price_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    current_price_currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="USD"
    )

    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    seller_notes: Mapped[str | None] = mapped_column(Text())
    expires_on: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True))
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    is_active = Column(Boolean, nullable=False, server_default="1")

    agency = relationship("Agency", back_populates="listings")
    favorites = relationship(
        "Favorite", back_populates="listing", cascade="all, delete-orphan"
    )
    purchases = relationship(
        "Purchase", back_populates="listing", cascade="all, delete-orphan"
    )

    car_model: Mapped["CarModel"] = relationship("CarModel", back_populates="listings")

    __table_args__ = (Index("ix_listings_brand_model", "brand", "model"),)
