"""
Service do Cliente.
É aqui que ficam as regras de negócio do cliente: o service chama o repository,
trata os casos especiais e devolve os dados prontos pro router.
"""

import re
from typing import Optional
from uuid import UUID

from app.schemas.client import Client, ClientCreate, ClientUpdate
from app.repositories import client as repo
from app.core.exceptions import ConflictError


def create(data: ClientCreate) -> Client:
    """Cria um cliente novo."""
    # O CPF não pode repetir. O banco já garante isso com o UNIQUE, mas eu checo
    # aqui antes pra devolver um 409 com mensagem boa, em vez do erro cru do driver
    # (que viraria um 500). O data.cpf já chega só com os dígitos, normalizado lá
    # no validador do ClientCreate.
    existing = repo.get_by_cpf(data.cpf)
    if existing is not None:
        # Mando junto QUEM é a aluna existente (id, nome, se está ativa). Assim a
        # UI pode oferecer reativar, em vez de só dizer "já existe". A decisão de
        # reativar é da recepção (a aluna pode ter pedido exclusão por LGPD).
        raise ConflictError(
            f"Já existe um cliente com o CPF {data.cpf}",
            conflict_with={
                "id": str(existing.id),
                "name": existing.name,
                "is_active": existing.is_active,
            },
        )
    return repo.create(data)


def get_all() -> list[Client]:
    """Lista todos os clientes."""
    return repo.get_all()


def get_by_id(client_id: UUID) -> Optional[Client]:
    """Busca um cliente pelo ID. Devolve None se não achar."""
    return repo.get_by_id(client_id)


def find_by_cpf(cpf: str) -> Optional[Client]:
    """Busca um cliente pelo CPF (pra recepção achar uma aluna que já existe).

    Normaliza a entrada pra só dígitos antes de consultar, então tanto faz vir
    "529.982.247-25" ou "52998224725". Devolve None se não achar.
    """
    digits = re.sub(r"\D", "", cpf)
    return repo.get_by_cpf(digits)


def update(client_id: UUID, data: ClientUpdate) -> Optional[Client]:
    """Atualiza um cliente que já existe."""
    # exclude_none=True manda pro banco só o que veio preenchido, então dá pra
    # mudar um campo só sem zerar o resto. mode="json" deixa os tipos (date,
    # datetime, UUID, Enum) no formato que o Supabase aceita.
    update_data = data.model_dump(mode="json", exclude_none=True)

    # Corpo vazio é erro de quem chamou, não nosso. Esse ValueError vira um
    # HTTP 400 lá no main.py (tem um handler que cuida disso).
    if not update_data:
        raise ValueError("Nenhum campo para atualizar")

    # Se o PUT mandar is_active=true, aproveito pra "ressuscitar" o registro
    # limpando o deleted_at. É o contrário do que o DELETE faz (soft-delete).
    if update_data.get("is_active") is True:
        update_data["deleted_at"] = None

    return repo.update(client_id, update_data)


def delete(client_id: UUID) -> bool:
    """Remove o cliente (soft-delete). True se removeu, False se o ID não existia."""
    return repo.delete(client_id)
