"""
Service do Cliente.
Camada de regras de negócio. Coordena chamadas ao repository, valida regras complexas e prepara dados.
"""

from typing import Optional
from uuid import UUID

from app.schemas.client import Client, ClientCreate, ClientUpdate
from app.repositories import client as repo


def create(data: ClientCreate) -> Client:
    """Cria novo cliente."""
    return repo.create(data)


def get_all() -> list[Client]:
    """Lista todos os clientes."""
    return repo.get_all()


def get_by_id(client_id: UUID) -> Optional[Client]:
    """Busca cliente por ID. Retorna None se não existir."""
    return repo.get_by_id(client_id)


def update(client_id: UUID, data: ClientUpdate) -> Optional[Client]:
    """Atualiza cliente existente."""
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

    return repo.update(client_id, update_data)


def delete(client_id: UUID) -> bool:
    """Remove cliente. Retorna True se removeu, False se não existia."""
    return repo.delete(client_id)
