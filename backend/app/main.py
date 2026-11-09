from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="FinWise API",
    description="Backend for personal finance goal tracking and AI-guided spending.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Simple liveness check — used by deployment platforms and docker-compose."""
    return {"status": "ok"}


# Routers are added here as each resource is built (Week 2+).
# from app.api.v1.endpoints import auth, goals, transactions
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(goals.router, prefix="/api/v1/goals", tags=["goals"])
# app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
