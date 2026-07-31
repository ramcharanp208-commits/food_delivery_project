from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine
import models
from config import settings
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="A production-quality food delivery backend API",
    version=settings.APP_VERSION,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from routers import auth, restaurants, menu, cart, orders

app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get("/api", tags=["Root"])
def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/auth",
            "restaurants": "/restaurants",
            "menu": "/restaurants/{restaurant_id}/items",
            "cart": "/cart",
            "orders": "/orders",
        },
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for Render."""
    return {"status": "healthy", "message": "API is running smoothly"}


# Serve frontend static files (must be after all API routes)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
