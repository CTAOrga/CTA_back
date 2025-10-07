from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models import user  # noqa: F401
from app.models import agency  # noqa: F401
from app.models import listing  # noqa: F401
from app.models import favorite  # noqa: F401
