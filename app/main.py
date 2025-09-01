from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.router import api_router

# NUEVO: crear tablas
from app.db.base import Base
from app.db.session import get_engine
import app.models.item
import app.models.agency  # ← nuevo
import app.models.user  # ← nuevo


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    engine = get_engine()
    Base.metadata.create_all(bind=engine)  # crea tablas si no existen
    try:
        yield
    finally:
        engine.dispose()  # opcional


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


app.include_router(api_router, prefix="/api/v1")
