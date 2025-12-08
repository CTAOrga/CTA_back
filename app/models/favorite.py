from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )

    customer = relationship("User", back_populates="favorites")
    listing = relationship("Listing", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint(
            "customer_id", "listing_id", name="uq_favorite_customer_listing"
        ),
    )
