from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.students.students_model import StudentModel
from app.students.students_schemas import Student


class StudentsSqlRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_all(self) -> list[Student]:
        statement = select(StudentModel)
        models = self.session.scalars(statement).all()

        return [self._to_schema(model) for model in models]

    def find_by_id(self, student_id: str) -> Student | None:
        student_uuid = self._to_uuid(student_id)

        if student_uuid is None:
            return None

        model = self.session.get(StudentModel, student_uuid)

        if model is None:
            return None

        return self._to_schema(model)

    def find_by_email(self, email: str) -> Student | None:
        statement = select(StudentModel).where(
            StudentModel.email == email
        )
        model = self.session.scalar(statement)

        if model is None:
            return None

        return self._to_schema(model)

    def find_by_username(self, username: str) -> Student | None:
        statement = select(StudentModel).where(
            StudentModel.username == username
        )
        model = self.session.scalar(statement)

        if model is None:
            return None

        return self._to_schema(model)

    def save(self, student: Student) -> Student:
        student_uuid = self._to_uuid(student.id)

        if student_uuid is None:
            raise ValueError(
                "El identificador del estudiante no es un UUID válido"
            )

        model = self.session.get(StudentModel, student_uuid)

        if model is None:
            model = StudentModel(
                id=student_uuid,
                name=student.name,
                username=student.username,
                email=str(student.email),
                age=student.age,
                created_at=student.createdAt,
                updated_at=student.updatedAt,
            )
            self.session.add(model)
        else:
            model.name = student.name
            model.username = student.username
            model.email = str(student.email)
            model.age = student.age
            model.updated_at = student.updatedAt

        self.session.flush()
        self.session.refresh(model)

        return self._to_schema(model)

    def delete(self, student_id: str) -> None:
        student_uuid = self._to_uuid(student_id)

        if student_uuid is None:
            return

        model = self.session.get(StudentModel, student_uuid)

        if model is not None:
            self.session.delete(model)
            self.session.flush()

    @staticmethod
    def _to_uuid(student_id: str) -> UUID | None:
        try:
            return UUID(student_id)
        except ValueError:
            return None

    @staticmethod
    def _to_schema(model: StudentModel) -> Student:
        return Student(
            id=str(model.id),
            name=model.name,
            username=model.username,
            email=model.email,
            age=model.age,
            createdAt=model.created_at,
            updatedAt=model.updated_at,
        )