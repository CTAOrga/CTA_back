from decimal import Decimal
from sqlalchemy import Integer, String, DateTime, Text, Numeric, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agency_id: Mapped[int] = mapped_column(
        ForeignKey("agencies.id", ondelete="CASCADE"), index=True
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

    agency = relationship("Agency", back_populates="listings")
    favorites = relationship(
        "Favorite", back_populates="listing", cascade="all, delete-orphan"
    )
    purchases = relationship(
        "Purchase", back_populates="listing", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_listings_brand_model", "brand", "model"),)
