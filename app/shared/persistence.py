from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.shared.exceptions import conflict


def conflict_for_integrity_error(exc: IntegrityError) -> HTTPException | None:
    constraint_name = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
    message = str(exc.orig).lower()

    if constraint_name == "uq_students_email" or "students.email" in message:
        return conflict({"email": {"message": "El correo electrónico ya está en uso"}})

    if constraint_name == "uq_students_username" or "students.username" in message:
        return conflict(
            {"username": {"message": "El nombre de usuario ya está en uso"}}
        )

    if constraint_name == "uq_pets_student_name" or (
        "pets.student_id" in message and "pets.name" in message
    ):
        return conflict({"name": {"message": "Ya tienes una mascota con ese nombre"}})

    return None
