from sqlalchemy import Integer, ForeignKey, String, SmallInteger, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    car_model_id: Mapped[int] = mapped_column(
        ForeignKey("car_models.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rating: Mapped[int] = mapped_column(
        SmallInteger, nullable=False
    )  # 1–5, por ejemplo
    comment: Mapped[str] = mapped_column(String(1000), nullable=True)

    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    car_model = relationship("CarModel", back_populates="reviews")
    author = relationship("User", back_populates="reviews")
