from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.models import Base
from app.pets.orm_models import PetRecord
from app.shared.database import get_db_session


@pytest.fixture
def client() -> Iterator[tuple[TestClient, Session]]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _) -> None:
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    app = create_app()

    def override_session() -> Iterator[Session]:
        with Session(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_db_session] = override_session
    with TestClient(app) as test_client, Session(engine) as session:
        yield test_client, session
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def _student_payload(**overrides: object) -> dict[str, object]:
    return {
        "name": "Ana Perez",
        "username": "ana_perez",
        "email": "ana@example.com",
        "age": 21,
        **overrides,
    }


def test_student_and_pet_are_persisted_and_student_delete_cascades(
    client: tuple[TestClient, Session],
) -> None:
    test_client, session = client
    created = test_client.post(
        "/api/students",
        json={
            **_student_payload(),
            "pets": [{"name": "Firulais", "species": "perro", "age": 3}],
        },
    )

    assert created.status_code == 201
    student_id = created.json()["data"]["id"]
    pets = test_client.get(f"/api/students/{student_id}/pets")
    assert pets.status_code == 200
    assert pets.json()["data"]["total"] == 1
    assert pets.json()["data"]["items"][0]["name"] == "Firulais"
    pet_id = pets.json()["data"]["items"][0]["id"]

    updated_student = test_client.patch(
        f"/api/students/{student_id}", json={"name": "Ana Maria"}
    )
    updated_pet = test_client.patch(
        f"/api/students/{student_id}/pets/{pet_id}", json={"age": 4}
    )
    assert updated_student.json()["data"]["name"] == "Ana Maria"
    assert updated_pet.json()["data"]["age"] == 4

    deleted = test_client.delete(f"/api/students/{student_id}")
    assert deleted.status_code == 200
    assert session.scalar(select(func.count()).select_from(PetRecord)) == 0


def test_failed_nested_pet_insert_rolls_back_student_and_pets(
    client: tuple[TestClient, Session],
) -> None:
    test_client, session = client
    response = test_client.post(
        "/api/students",
        json={
            **_student_payload(),
            "pets": [
                {"name": "Michi", "species": "gato"},
                {"name": "Michi", "species": "gato"},
            ],
        },
    )

    assert response.status_code == 409
    assert response.json()["errors"]["name"]["message"] == (
        "Ya tienes una mascota con ese nombre"
    )
    assert test_client.get("/api/students").json()["data"]["total"] == 0
    assert session.scalar(select(func.count()).select_from(PetRecord)) == 0
