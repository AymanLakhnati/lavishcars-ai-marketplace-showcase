import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lavishcars.db")
if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL.split("://", 1)[1]
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {},
    pool_pre_ping=True,
    **(
        {"poolclass": NullPool}
        if os.getenv("DB_NULL_POOL") == "1" or os.getenv("VERCEL")
        else {}
    ),
)
if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as session:
        yield session
