"""Crear tabla de estudiantes.

Revision ID: fd9e8d31c935
Revises:
Create Date: 2026-10-28 19:35:45.200129
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# Identificadores utilizados por Alembic.
revision: str = "fd9e8d31c935"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear la tabla de estudiantes."""
    op.create_table(
        "students",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("username", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "age >= 18 AND age <= 99",
            name="ck_students_age_range",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_students_email"),
        "students",
        ["email"],
        unique=True,
    )
    op.create_index(
        op.f("ix_students_username"),
        "students",
        ["username"],
        unique=True,
    )


def downgrade() -> None:
    """Eliminar la tabla de estudiantes."""
    op.drop_index(
        op.f("ix_students_username"),
        table_name="students",
    )
    op.drop_index(
        op.f("ix_students_email"),
        table_name="students",
    )
    op.drop_table("students")