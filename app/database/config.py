import os

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://taller_user:"
    "cambia-esta-clave-local@127.0.0.1:5432/taller_db"
)


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)