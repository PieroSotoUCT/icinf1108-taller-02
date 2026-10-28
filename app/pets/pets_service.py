from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.pets.orm_models import PetRecord
from app.pets.pets_repository import PetsRepository
from app.pets.pets_schemas import CreatePetDto, Pet, PetList, UpdatePetDto
from app.shared.datetimes import utc_now
from app.shared.exceptions import conflict
from app.shared.persistence import conflict_for_integrity_error
from app.students.students_service import StudentsService, students_service


class PetsService:
    def __init__(self, repository: PetsRepository, students: StudentsService) -> None:
        self.repository = repository
        self.students_service = students

    def find_all_for_student(self, session: Session, student_id: str) -> PetList:
        self.students_service.find_by_id(session, student_id)
        pets = sorted(
            self.repository.find_all_by_student(session, student_id),
            key=lambda pet: pet.createdAt,
            reverse=True,
        )
        return PetList(
            total=len(pets),
            items=[Pet.model_validate(pet) for pet in pets],
        )

    def create(self, session: Session, student_id: str, data: CreatePetDto) -> Pet:
        try:
            with session.begin():
                self.students_service.find_by_id(session, student_id)
                self.assert_no_conflicts(session, student_id, data)
                now = utc_now()
                pet = PetRecord(
                    id=str(uuid4()),
                    studentId=student_id,
                    name=data.name,
                    species=data.species,
                    age=data.age,
                    createdAt=now,
                    updatedAt=now,
                )
                self.repository.save(session, pet)
        except IntegrityError as exc:
            self._raise_integrity_conflict(exc)
        return Pet.model_validate(pet)

    def update(
        self, session: Session, student_id: str, pet_id: str, data: UpdatePetDto
    ) -> Pet:
        try:
            with session.begin():
                existing = self._find_owned_record(session, student_id, pet_id)
                self.assert_no_conflicts(session, student_id, data, except_id=pet_id)
                for field, value in data.model_dump(exclude_none=True).items():
                    setattr(existing, field, value)
                existing.updatedAt = utc_now()
                session.flush()
        except IntegrityError as exc:
            self._raise_integrity_conflict(exc)
        return Pet.model_validate(existing)

    def delete(self, session: Session, student_id: str, pet_id: str) -> Pet:
        with session.begin():
            existing = self._find_owned_record(session, student_id, pet_id)
            pet = Pet.model_validate(existing)
            self.repository.delete(session, existing)
        return pet

    def find_owned(self, session: Session, student_id: str, pet_id: str) -> Pet:
        return Pet.model_validate(self._find_owned_record(session, student_id, pet_id))

    def _find_owned_record(
        self, session: Session, student_id: str, pet_id: str
    ) -> PetRecord:
        self.students_service.find_by_id(session, student_id)
        pet = self.repository.find_by_id(session, pet_id)
        if pet is None or pet.studentId != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada",
            )
        return pet

    def assert_no_conflicts(
        self,
        session: Session,
        student_id: str,
        data: CreatePetDto | UpdatePetDto,
        except_id: str | None = None,
    ) -> None:
        if not data.name:
            return
        existing = self.repository.find_by_student_and_name(
            session, student_id, data.name
        )
        if existing and existing.id != except_id:
            raise conflict(
                {"name": {"message": "Ya tienes una mascota con ese nombre"}}
            )

    def _raise_integrity_conflict(self, exc: IntegrityError) -> None:
        error = conflict_for_integrity_error(exc)
        if error is None:
            raise exc
        raise error from exc


pets_repository = PetsRepository()
pets_service = PetsService(pets_repository, students_service)
