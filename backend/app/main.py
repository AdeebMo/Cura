from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.bootstrap import get_consultation_service
from app.core.config import settings

app = FastAPI(
    title="Cura API",
    version="0.1.0",
    description="Educational rule-based symptom triage and diagnostic assistant",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
def startup() -> None:
    get_consultation_service()


app.include_router(router)
