import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.dashboard import router as dashboard_router
from app.api.influencers import router as influencers_router
from app.core.config import settings
from app.core.database import create_tables

app = FastAPI(
    title=settings.APP_NAME,
    description="Influencer reputation analysis tool for Instagram and TikTok",
    version="1.0.0",
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded screenshots
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=static_dir), name="uploads")

# Include routers
app.include_router(influencers_router)
app.include_router(dashboard_router)


@app.on_event("startup")
async def startup():
    await create_tables()


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
