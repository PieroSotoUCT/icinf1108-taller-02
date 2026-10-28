from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.pets.pets_repository import pets_repository
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)
from app.students.students_service import StudentsService
from app.students.students_sql_repository import StudentsSqlRepository

router = APIRouter(prefix="/api/students", tags=["Students"])

DatabaseSession = Annotated[Session, Depends(get_db)]


def create_students_service(session: Session) -> StudentsService:
    repository = StudentsSqlRepository(session)

    return StudentsService(
        repository=repository,
        pets=pets_repository,
    )


@router.get("")
def find_all(session: DatabaseSession) -> StudentList:
    service = create_students_service(session)

    return service.find_all()


@router.get("/{studentId}")
def find_by_id(
    studentId: str,
    session: DatabaseSession,
) -> Student:
    service = create_students_service(session)

    return service.find_by_id(studentId)


@router.post("", status_code=status.HTTP_201_CREATED)
def create(
    body: CreateStudentDto,
    session: DatabaseSession,
) -> Student:
    if body.pets:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "La creación conjunta de estudiantes y mascotas "
                "estará disponible al integrar el ORM de mascotas"
            ),
        )

    service = create_students_service(session)

    try:
        student = service.create(body)
        session.commit()

        return student
    except Exception:
        session.rollback()
        raise


@router.patch("/{studentId}")
def update(
    studentId: str,
    body: UpdateStudentDto,
    session: DatabaseSession,
) -> Student:
    service = create_students_service(session)

    try:
        student = service.update(studentId, body)
        session.commit()

        return student
    except Exception:
        session.rollback()
        raise


@router.delete("/{studentId}")
def delete(
    studentId: str,
    session: DatabaseSession,
) -> Student:
    service = create_students_service(session)

    try:
        student = service.delete(studentId)
        session.commit()

        return student
    except Exception:
        session.rollback()
        raise