from datetime import datetime, time
from typing import Optional

from fastapi import HTTPException, status


def _parse_date_param(value: Optional[str]) -> Optional[datetime]:
    """
    value viene como 'YYYY-MM-DD' desde el front.
    Lo convertimos a datetime a las 00:00, para usar en filtros >= / <=.
    """
    if not value:
        return None
    try:
        d = datetime.fromisoformat(value).date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fecha inválida: {value}. Formato esperado YYYY-MM-DD.",
        )
    return datetime.combine(d, time.min)
