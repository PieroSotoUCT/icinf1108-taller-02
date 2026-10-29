"""Configuración compartida de la conexión y las sesiones ORM."""

import os
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def get_database_url() -> URL:
    """Construye la URL sin exponer la contraseña en los archivos del proyecto."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return make_url(database_url)

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DB")
    if not all((user, password, database)):
        raise RuntimeError("Faltan POSTGRES_USER, POSTGRES_PASSWORD o POSTGRES_DB")

    return URL.create(
        "postgresql+psycopg",
        username=user,
        password=password,
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=database,
    )


@lru_cache
def get_engine() -> Engine:
    """Reutiliza un único pool de conexiones por proceso de la API."""
    url = get_database_url()
    connect_args = (
        {"connect_timeout": 3} if url.drivername.startswith("postgresql") else {}
    )
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_db_session() -> Iterator[Session]:
    with get_session_factory()() as session:
        yield session
