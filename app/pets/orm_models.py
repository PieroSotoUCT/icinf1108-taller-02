from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.orm import Base

if TYPE_CHECKING:
    from app.students.orm_models import StudentRecord


class PetRecord(Base):
    __tablename__ = "pets"
    __table_args__ = (
        UniqueConstraint("student_id", "name", name="uq_pets_student_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    studentId: Mapped[str] = mapped_column(
        "student_id",
        String(36),
        ForeignKey(
            "students.id",
            name="fk_pets_student_id_students",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int | None] = mapped_column(nullable=True)
    createdAt: Mapped[datetime] = mapped_column(
        "created_at", DateTime(timezone=True), nullable=False
    )
    updatedAt: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), nullable=False
    )
    student: Mapped[StudentRecord] = relationship(back_populates="pets")
