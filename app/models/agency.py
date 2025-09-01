from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Agency(Base):
    __tablename__ = "agencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
