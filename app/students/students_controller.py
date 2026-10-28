from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.shared.database import get_db_session
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)
from app.students.students_service import students_service

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("")
def find_all(session: Annotated[Session, Depends(get_db_session)]) -> StudentList:
    return students_service.find_all(session)


@router.get("/{studentId}")
def find_by_id(
    studentId: str, session: Annotated[Session, Depends(get_db_session)]
) -> Student:
    return students_service.find_by_id(session, studentId)


@router.post("", status_code=201)
def create(
    body: CreateStudentDto, session: Annotated[Session, Depends(get_db_session)]
) -> Student:
    return students_service.create(session, body)


@router.patch("/{studentId}")
def update(
    studentId: str,
    body: UpdateStudentDto,
    session: Annotated[Session, Depends(get_db_session)],
) -> Student:
    return students_service.update(session, studentId, body)


@router.delete("/{studentId}")
def delete(
    studentId: str, session: Annotated[Session, Depends(get_db_session)]
) -> Student:
    return students_service.delete(session, studentId)
