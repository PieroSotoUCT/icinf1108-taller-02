from sqlalchemy import select
from sqlalchemy.orm import Session

from app.students.orm_models import StudentRecord


class StudentsRepository:
    def find_all(self, session: Session) -> list[StudentRecord]:
        return list(session.scalars(select(StudentRecord)).all())

    def find_by_id(self, session: Session, student_id: str) -> StudentRecord | None:
        return session.get(StudentRecord, student_id)

    def find_by_email(self, session: Session, email: str) -> StudentRecord | None:
        return session.scalar(select(StudentRecord).where(StudentRecord.email == email))

    def find_by_username(self, session: Session, username: str) -> StudentRecord | None:
        return session.scalar(
            select(StudentRecord).where(StudentRecord.username == username)
        )

    def save(self, session: Session, student: StudentRecord) -> StudentRecord:
        session.add(student)
        session.flush()
        return student

    def delete(self, session: Session, student: StudentRecord) -> None:
        session.delete(student)
        session.flush()
