from sqlalchemy import ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    agency_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("agencies.id", ondelete="CASCADE"),
        nullable=False,
    )
    car_model_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("car_models.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    agency = relationship("Agency", back_populates="inventory_items")
    car_model = relationship("CarModel", back_populates="inventory_items")
