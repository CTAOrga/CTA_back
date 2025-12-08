from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.router import api_router

from app.db.base import Base
from app.db.session import get_engine
import app.models.agency  # ← nuevo
import app.models.user  # ← nuevo
from sqlalchemy.exc import SQLAlchemyError
from app.core.logging_config import setup_logging
import logging
from prometheus_fastapi_instrumentator import Instrumentator


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    engine = get_engine()
    try:
        if settings.APP_ENV != "test":
            Base.metadata.create_all(bind=engine)  # crea tablas si no existen
    except SQLAlchemyError as e:
        # Loguea y repropaga para que el contenedor reinicie si corresponde
        print(f"[DB] Error creando tablas: {e}")
        raise
    try:
        logging.info("Startup complete. Metrics exposed.")
        yield
    finally:
        engine.dispose()  # opcional


setup_logging()
app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


app.include_router(api_router, prefix="/api/v1")
