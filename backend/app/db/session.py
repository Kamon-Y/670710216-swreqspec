import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def create_database_engine(database_url: str | None = None) -> Engine:
    # รองรับ CON-TECH-01 โดยเลือกฐานข้อมูลผ่าน DATABASE_URL
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///booking.db")
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


engine = create_database_engine()