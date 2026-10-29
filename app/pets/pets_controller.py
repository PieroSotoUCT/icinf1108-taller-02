from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.pets.pets_schemas import CreatePetDto, Pet, PetList, UpdatePetDto
from app.pets.pets_service import pets_service
from app.shared.database import get_db_session

router = APIRouter(
    prefix="/api/students/{studentId}/pets",
    tags=["Pets"],
)


@router.get("")
def find_all(
    studentId: str, session: Annotated[Session, Depends(get_db_session)]
) -> PetList:
    return pets_service.find_all_for_student(session, studentId)


@router.post("", status_code=201)
def create(
    studentId: str,
    body: CreatePetDto,
    session: Annotated[Session, Depends(get_db_session)],
) -> Pet:
    return pets_service.create(session, studentId, body)


@router.patch("/{petId}")
def update(
    studentId: str,
    petId: str,
    body: UpdatePetDto,
    session: Annotated[Session, Depends(get_db_session)],
) -> Pet:
    return pets_service.update(session, studentId, petId, body)


@router.delete("/{petId}")
def delete(
    studentId: str,
    petId: str,
    session: Annotated[Session, Depends(get_db_session)],
) -> Pet:
    return pets_service.delete(session, studentId, petId)
