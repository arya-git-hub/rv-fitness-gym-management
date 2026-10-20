"""
app/main.py
FastAPI application entry point.

To add a new module router, add ONE line in the "Register module routers" section:
    app.include_router(your_module.router, prefix="/api")
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

app = FastAPI(
    title="RV Fitness API",
    description="Gym Management System — Narsobawadi",
    version="1.0.0",
    # Hide docs in production
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)

# ---------------------------------------------------------------------------
# CORS — allow the Vite dev server and deployed frontend
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev
        "http://localhost:3000",
        # Add your Vercel / Netlify URL here when deploying
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global error handler — never expose stack traces
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# ---------------------------------------------------------------------------
# Health check (public — used by deployment platforms)
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok", "env": settings.APP_ENV}


# ---------------------------------------------------------------------------
# Register module routers (one line per module — each person adds theirs here)
# ---------------------------------------------------------------------------
# from app.modules.members import router as members_router
# app.include_router(members_router.router, prefix="/api")

# from app.modules.billing import router as billing_router
# app.include_router(billing_router.router, prefix="/api")

# from app.modules.trainers import router as trainers_router
# app.include_router(trainers_router.router, prefix="/api")

# from app.modules.content import router as content_router
# app.include_router(content_router.router, prefix="/api")

from app.modules.workouts import router as workouts_router
app.include_router(workouts_router, prefix="/api")
