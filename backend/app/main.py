from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.users import router as users_router
from app.api.v1.auth import router as auth_router
from app.api.v1.processes import router as processes_router
from app.api.v1.risks import router as risks_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.audit import router as audit_router

app = FastAPI(
    title=settings.app_name,
    description="Plataforma inteligente de gestao de processos e riscos.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(processes_router)
app.include_router(risks_router)
app.include_router(dashboard_router)
app.include_router(audit_router)


@app.get("/")
def root():
    return {"status": "ok", "app": settings.app_name}


@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": settings.environment}
