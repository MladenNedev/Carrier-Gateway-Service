from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.persistence.session import get_db

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health():
    return {"status": "ok"}

@router.get("/db")
def health_db(db: Session = Depends(get_db)):
    db.execute("SELECT 1")
    return {"database": "ok"}