"""
Service do Instructor.
É aqui que ficam as regras de negócio do instrutor: o service chama o repository,
trata os casos especiais e devolve os dados prontos pro router.
"""

from typing import Optional
from uuid import UUID

from app.schemas.instructor import Instructor, InstructorCreate, InstructorUpdate
from app.repositories import instructor as repo


def create(data: InstructorCreate) -> Instructor:
    """Cria um instrutor novo."""
    return repo.create(data)


def get_all() -> list[Instructor]:
    """Lista todos os instrutores."""
    return repo.get_all()


def get_by_id(instructor_id: UUID) -> Optional[Instructor]:
    """Busca um instrutor pelo ID. Devolve None se não achar."""
    return repo.get_by_id(instructor_id)


def update(instructor_id: UUID, data: InstructorUpdate) -> Optional[Instructor]:
    """Atualiza um instrutor que já existe."""
    # exclude_none=True manda pro banco só o que veio preenchido, então dá pra
    # mudar um campo só sem zerar o resto. mode="json" deixa os tipos (date,
    # datetime, UUID, Enum) no formato que o Supabase aceita.
    update_data = data.model_dump(mode="json", exclude_none=True)

    # Corpo vazio é erro de quem chamou, não nosso. Esse ValueError vira um
    # HTTP 400 lá no main.py (tem um handler que cuida disso).
    if not update_data:
        raise ValueError("Nenhum campo para atualizar")

    # Regra do CREFITO: como o update é parcial, pra saber se "has_credential=True
    # exige credential_number" eu preciso olhar o estado final (o que veio no PUT +
    # o que já está salvo no banco), não só o payload. Só vou no banco se o update
    # mexeu na credencial — senão seria uma consulta à toa.
    if "has_credential" in update_data or "credential_number" in update_data:
        current = repo.get_by_id(instructor_id)
        if current is None:
            return None  # não achou o instrutor; o router devolve 404

        effective_has_credential = update_data.get("has_credential", current.has_credential)
        effective_credential_number = update_data.get("credential_number", current.credential_number)

        if effective_has_credential and not effective_credential_number:
            raise ValueError("credential_number é obrigatório quando has_credential=True")

    # Se o PUT mandar is_active=true, aproveito pra "ressuscitar" o registro
    # limpando o deleted_at. É o contrário do que o DELETE faz (soft-delete).
    if update_data.get("is_active") is True:
        update_data["deleted_at"] = None

    return repo.update(instructor_id, update_data)


def delete(instructor_id: UUID) -> bool:
    """Remove o instrutor (soft-delete). True se removeu, False se o ID não existia."""
    return repo.delete(instructor_id)
