# app/models/car_model.py
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CarModel(Base):
    __tablename__ = "car_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    # Podés sumar year, version, etc. según el UML:
    # year: Mapped[int] = mapped_column(Integer, nullable=True)

    listings = relationship("Listing", back_populates="car_model")
    reviews = relationship("Review", back_populates="car_model")

    inventory_items = relationship(
        "Inventory",
        back_populates="car_model",
        cascade="all, delete-orphan",
    )
