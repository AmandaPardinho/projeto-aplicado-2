"""
Service do Instructor.
Camada de regras de negócio. Coordena chamadas ao repository, valida regras complexas e prepara dados.
"""

from typing import Optional
from uuid import UUID

from app.schemas.instructor import Instructor, InstructorCreate, InstructorUpdate
from app.repositories import instructor as repo


def create(data: InstructorCreate) -> Instructor:
    """Cria novo instrutor."""
    return repo.create(data)


def get_all() -> list[Instructor]:
    """Lista todos os instrutores."""
    return repo.get_all()


def get_by_id(instructor_id: UUID) -> Optional[Instructor]:
    """Busca instrutor por ID. Retorna None se não existir."""
    return repo.get_by_id(instructor_id)


def update(instructor_id: UUID, data: InstructorUpdate) -> Optional[Instructor]:
    """Atualiza instrutor existente."""
    # exclude_none=True: só envia ao banco os campos que o usuário preencheu (PATCH-like).
    # mode="json": serializa date/datetime/UUID/Enum em strings JSON-compatíveis.
    update_data = data.model_dump(mode="json", exclude_none=True)

    # Input vazio é erro do CLIENTE, não do servidor.
    # ValueError vira HTTP 400 via exception handler global registrado no main.py.
    if not update_data:
        raise ValueError("Nenhum campo para atualizar")

    # Reativação automática: se vier is_active=true no PUT, limpa deleted_at
    # (operação inversa do soft-delete feito pelo DELETE).
    if update_data.get("is_active") is True:
        update_data["deleted_at"] = None

    return repo.update(instructor_id, update_data)


def delete(instructor_id: UUID) -> bool:
    """Remove instrutor. Retorna True se removeu, False se não existia."""
    return repo.delete(instructor_id)
