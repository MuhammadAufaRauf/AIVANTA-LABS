from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.workforce import router as workforce_router
from app.core.config import get_settings
from app.db import models  # noqa: F401 - registers SQLAlchemy models
from app.db.migrations import migrate_legacy_tables
from app.db.session import Base, SessionLocal, engine
from app.services.workforce import seed_workforce

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    migrate_legacy_tables(engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.get(models.CompanyConfig, 1) is None:
            db.add(models.CompanyConfig(id=1))
            db.commit()
        seed_workforce(db)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_v1_prefix)
app.include_router(workforce_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "Aivanta OS API", "docs": "/docs", "health": f"{settings.api_v1_prefix}/health"}
