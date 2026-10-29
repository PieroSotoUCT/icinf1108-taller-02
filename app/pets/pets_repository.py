from sqlalchemy import select
from sqlalchemy.orm import Session

from app.pets.orm_models import PetRecord


class PetsRepository:
    def find_all_by_student(self, session: Session, student_id: str) -> list[PetRecord]:
        return list(
            session.scalars(
                select(PetRecord).where(PetRecord.studentId == student_id)
            ).all()
        )

    def find_by_id(self, session: Session, pet_id: str) -> PetRecord | None:
        return session.get(PetRecord, pet_id)

    def find_by_student_and_name(
        self, session: Session, student_id: str, name: str
    ) -> PetRecord | None:
        return session.scalar(
            select(PetRecord).where(
                PetRecord.studentId == student_id, PetRecord.name == name
            )
        )

    def save(self, session: Session, pet: PetRecord) -> PetRecord:
        session.add(pet)
        session.flush()
        return pet

    def delete(self, session: Session, pet: PetRecord) -> None:
        session.delete(pet)
        session.flush()
