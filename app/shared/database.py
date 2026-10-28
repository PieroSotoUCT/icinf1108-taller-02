"""Configuración de conexión PostgreSQL compartida con la futura capa ORM."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def get_database_url() -> URL:
    """Construye la URL sin exponer la contraseña en los archivos del proyecto."""
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
    return create_engine(
        get_database_url(), pool_pre_ping=True, connect_args={"connect_timeout": 3}
    )
