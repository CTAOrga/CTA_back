# app/models/purchase.py
from decimal import Decimal
from sqlalchemy import Integer, DateTime, ForeignKey, Numeric, String, text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from enum import Enum as PyEnum


class PurchaseStatus(str, PyEnum):
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id", ondelete="CASCADE"), index=True
    )

    unit_price_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    unit_price_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    status: Mapped[PurchaseStatus] = mapped_column(
        Enum(PurchaseStatus, name="purchase_status"),
        nullable=False,
        default=PurchaseStatus.COMPLETED,
    )

    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    buyer = relationship("User", back_populates="purchases")
    listing = relationship("Listing", back_populates="purchases")
