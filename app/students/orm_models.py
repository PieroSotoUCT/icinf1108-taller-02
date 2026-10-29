from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.orm import Base

if TYPE_CHECKING:
    from app.pets.orm_models import PetRecord


class StudentRecord(Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("email", name="uq_students_email"),
        UniqueConstraint("username", name="uq_students_username"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        "created_at", DateTime(timezone=True), nullable=False
    )
    updatedAt: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), nullable=False
    )
    pets: Mapped[list[PetRecord]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
