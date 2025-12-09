from sqlalchemy import Integer, String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Agency(Base):
    __tablename__ = "agencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )

    listings = relationship(
        "Listing", back_populates="agency", cascade="all, delete-orphan"
    )

    inventory_items = relationship(
        "Inventory",
        back_populates="agency",
        cascade="all, delete-orphan",
    )
