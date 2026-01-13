from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health_check():
    return {"status": "ok"}

from app.api.v1.shipments import router as shipments_router

app.include_router(shipments_router)