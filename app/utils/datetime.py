# app/utils/datetime.py
from datetime import datetime
from typing import Optional, Union

from fastapi import HTTPException, status


def parse_expires_on(value: Optional[Union[str, datetime]]) -> Optional[datetime]:
    """
    Normaliza el expires_on que viene en el payload a un datetime de Python.

    Acepta:
    - None
    - datetime ya parseado
    - string ISO tipo "2026-01-01T00:00:00.000Z" o sin Z
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    # En este punto asumimos string
    value_str = value

    # Ejemplo que llega del front: "2026-01-01T00:00:00.000Z"
    # Quitamos la Z (timezone) para usar datetime "naive"
    if value_str.endswith("Z"):
        value_str = value_str[:-1]

    try:
        # fromisoformat acepta "YYYY-MM-DDTHH:MM:SS" y también con milisegundos
        return datetime.fromisoformat(value_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido para expires_on.",
        )
