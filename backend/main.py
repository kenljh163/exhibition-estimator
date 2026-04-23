"""
展厅智能概算系统 - FastAPI 主入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, SessionLocal
from app.models.models import Base
from app.services.seed_data import seed_initial_data
from app.api.estimation import router as estimation_router
from app.api.admin import router as admin_router
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时初始化数据库和种子数据"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="展厅智能概算系统",
    description="Exhibition Smart Estimator API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS配置
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(estimation_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {"message": "展厅智能概算系统 API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
