from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL（生产）/ SQLite（本地开发），通过 .env 或环境变量切换
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://estimator:estimator123@localhost:5432/estimator_db"
)

# SQLite 需要 check_same_thread=False，PostgreSQL 不需要
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
