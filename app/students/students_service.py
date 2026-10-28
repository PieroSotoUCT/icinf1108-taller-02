from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.pets.orm_models import PetRecord
from app.pets.pets_schemas import CreatePetDto
from app.shared.datetimes import utc_now
from app.shared.exceptions import conflict
from app.shared.persistence import conflict_for_integrity_error
from app.shared.types import FieldErrors
from app.students.orm_models import StudentRecord
from app.students.students_repository import StudentsRepository
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)


class StudentsService:
    def __init__(self, repository: StudentsRepository) -> None:
        self.repository = repository

    def find_all(self, session: Session) -> StudentList:
        students = sorted(
            self.repository.find_all(session),
            key=lambda student: student.createdAt,
            reverse=True,
        )
        return StudentList(
            total=len(students),
            items=[Student.model_validate(student) for student in students],
        )

    def find_by_id(self, session: Session, student_id: str) -> Student:
        student = self.repository.find_by_id(session, student_id)
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )
        return Student.model_validate(student)

    def create(self, session: Session, data: CreateStudentDto) -> Student:
        try:
            with session.begin():
                self.assert_no_conflicts(session, data)
                now = utc_now()
                student = StudentRecord(
                    id=str(uuid4()),
                    name=data.name,
                    username=data.username,
                    email=str(data.email),
                    age=data.age,
                    createdAt=now,
                    updatedAt=now,
                )
                for pet_data in data.pets:
                    student.pets.append(
                        self._create_pet_record(student.id, pet_data, now)
                    )

                self.repository.save(session, student)
        except IntegrityError as exc:
            self._raise_integrity_conflict(exc)

        return Student.model_validate(student)

    def update(
        self, session: Session, student_id: str, data: UpdateStudentDto
    ) -> Student:
        try:
            with session.begin():
                existing = self._find_record(session, student_id)
                self.assert_no_conflicts(session, data, except_id=student_id)
                for field, value in data.model_dump(exclude_none=True).items():
                    setattr(existing, field, value)
                existing.updatedAt = utc_now()
                session.flush()
        except IntegrityError as exc:
            self._raise_integrity_conflict(exc)

        return Student.model_validate(existing)

    def delete(self, session: Session, student_id: str) -> Student:
        with session.begin():
            existing = self._find_record(session, student_id)
            student = Student.model_validate(existing)
            self.repository.delete(session, existing)
        return student

    def assert_no_conflicts(
        self,
        session: Session,
        data: CreateStudentDto | UpdateStudentDto,
        except_id: str | None = None,
    ) -> None:
        errors: FieldErrors = {}

        if data.email:
            existing = self.repository.find_by_email(session, str(data.email))
            if existing and existing.id != except_id:
                errors["email"] = {"message": "El correo electrónico ya está en uso"}

        if data.username:
            existing = self.repository.find_by_username(session, data.username)
            if existing and existing.id != except_id:
                errors["username"] = {"message": "El nombre de usuario ya está en uso"}

        if errors:
            raise conflict(errors)

    def _find_record(self, session: Session, student_id: str) -> StudentRecord:
        student = self.repository.find_by_id(session, student_id)
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )
        return student

    def _raise_integrity_conflict(self, exc: IntegrityError) -> None:
        error = conflict_for_integrity_error(exc)
        if error is None:
            raise exc
        raise error from exc

    @staticmethod
    def _create_pet_record(
        student_id: str, data: CreatePetDto, now: datetime
    ) -> PetRecord:
        return PetRecord(
            id=str(uuid4()),
            studentId=student_id,
            name=data.name,
            species=data.species,
            age=data.age,
            createdAt=now,
            updatedAt=now,
        )


students_repository = StudentsRepository()
students_service = StudentsService(students_repository)
