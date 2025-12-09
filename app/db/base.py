from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models import user  # noqa: F401
from app.models import agency  # noqa: F401
from app.models import listing  # noqa: F401
from app.models import favorite  # noqa: F401
from app.models import purchase  # noqa: F401
from app.models import car_model  # noqa: F401
from app.models import review  # noqa: F401
from app.models import inventory  # noqa: F401
