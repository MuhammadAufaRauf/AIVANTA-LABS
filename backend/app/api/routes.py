from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import models  # noqa: F401 - registers SQLAlchemy models
from app.db.session import Base, engine, get_db
from app.schemas import CompanyConfigRead

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


@router.get("/company", response_model=CompanyConfigRead)
def get_company(db: Session = Depends(get_db)) -> models.CompanyConfig:
    Base.metadata.create_all(bind=engine)
    company = db.get(models.CompanyConfig, 1)
    if company is None:
        company = models.CompanyConfig(id=1)
        db.add(company)
        db.commit()
        db.refresh(company)
    return company


@router.get("/system-info")
def get_system_info() -> dict[str, str]:
    settings = get_settings()
    return {"product": "Aivanta OS", "environment": settings.app_env, "phase": "Phase 1 - Foundation"}
