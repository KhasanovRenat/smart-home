import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


engine = create_engine(
    URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER", "admin"),
        password=os.environ["DB_PASSWORD"],
        host=os.getenv("DB_HOST", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "smarthome_db"),
        query={"sslmode": os.getenv("DB_SSLMODE", "prefer")},
    ),
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)
SessionLocal = sessionmaker(engine)


def get_db():
    with SessionLocal() as session:
        yield session
