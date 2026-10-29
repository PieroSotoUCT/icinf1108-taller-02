from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.pets.pets_controller import router as pets_router
from app.shared.api_response import envelope_middleware
from app.shared.database import get_engine
from app.shared.exceptions import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.students.students_controller import router as students_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="FastAPI CRUD Students & Pets",
        description=("API CRUD de estudiantes y sus mascotas con persistencia ORM"),
        version="1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    app.middleware("http")(envelope_middleware)

    app.include_router(students_router)
    app.include_router(pets_router)

    @app.get("/health/db")
    def database_health() -> dict[str, str]:
        try:
            with get_engine().connect() as connection:
                connection.execute(text("SELECT 1"))
        except (RuntimeError, ValueError, SQLAlchemyError) as exc:
            raise HTTPException(
                status_code=503, detail="No se pudo conectar a PostgreSQL"
            ) from exc
        return {"database": "ok"}

    @app.api_route(
        "/api/{path:path}",
        methods=["GET", "POST", "PATCH", "DELETE", "PUT", "OPTIONS", "HEAD"],
    )
    def not_found_api(request: Request, path: str) -> None:
        raise HTTPException(
            status_code=404, detail=f"Cannot {request.method} /api/{path}"
        )

    app.mount("/", StaticFiles(directory="public", html=True), name="static")

    return app


app = create_app()
