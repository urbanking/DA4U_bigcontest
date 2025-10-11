"""
FastAPI 엔트리포인트
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.logger import logger
from backend.routers import (
    store_routes,
    metrics_routes,
    diagnostic_routes,
    marketing_routes,
    orchestrator_routes
)

app = FastAPI(
    title="BigContest AI Agent API",
    description="LangGraph 기반 멀티에이전트 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(store_routes.router, prefix="/api/store", tags=["Store"])
app.include_router(metrics_routes.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(diagnostic_routes.router, prefix="/api/diagnostic", tags=["Diagnostic"])
app.include_router(marketing_routes.router, prefix="/api/marketing", tags=["Marketing"])
app.include_router(orchestrator_routes.router, prefix="/api/run", tags=["Orchestrator"])


@app.get("/")
async def root():
    """헬스체크"""
    return {"status": "ok", "message": "BigContest AI Agent API is running"}


@app.on_event("startup")
async def startup_event():
    logger.info("Starting BigContest AI Agent API...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down BigContest AI Agent API...")

