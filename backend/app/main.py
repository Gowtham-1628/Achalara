"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.models import (  # noqa: F401  — side-effect imports to register models with SQLAlchemy metadata
    Client,
    Account,
    Strategy,
    Sleeve,
    Trade,
    Position,
    SyncLog,
    SheetSyncConfig,
)
from app.api.routes import clients, accounts, strategies, sleeves, trades, admin

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Schema is managed exclusively by Alembic (`alembic upgrade head`). The app no
# longer auto-creates tables — run migrations against Postgres before starting.


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle handler"""
    logger.info("Application starting...")
    if settings.scheduler_enabled:
        from app.services.scheduler import start_scheduler

        start_scheduler()
    yield
    if settings.scheduler_enabled:
        from app.services.scheduler import stop_scheduler

        stop_scheduler()
    logger.info("Application shutting down...")


app = FastAPI(
    title="Portfolio Management System",
    description="Backend API for portfolio management",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(clients.router, prefix="/api/v1/clients", tags=["clients"])
app.include_router(accounts.router, prefix="/api/v1/clients", tags=["accounts"])
app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["strategies"])
app.include_router(sleeves.router, prefix="/api/v1/clients", tags=["sleeves"])
app.include_router(trades.router, prefix="/api/v1/trades", tags=["trades"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "environment": settings.python_env}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Portfolio Management System",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.python_env == "development",
    )
