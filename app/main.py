from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title="Carrier Gateway Service")

from app.api.v1.merchants import router as merchants_router
from app.api.v1.shipments import router as shipments_router
from app.api.v1.health import router as health_router

app.include_router(merchants_router, prefix="/api/v1")
app.include_router(shipments_router, prefix="/api/v1")
app.include_router(health_router)