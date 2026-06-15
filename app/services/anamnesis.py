"""
Service da Anamnesis.
É aqui que ficam as regras de negócio da anamnese: o service chama o repository,
trata os casos especiais e devolve os dados prontos pro router.
"""

from typing import Optional
from uuid import UUID

from app.schemas.anamnesis import Anamnesis, AnamnesisCreate, AnamnesisUpdate
from app.repositories import anamnesis as repo
from app.repositories import client as client_repo
from app.core.exceptions import ConflictError, NotFoundError


def create(data: AnamnesisCreate) -> Anamnesis:
    """Cria a anamnese de um cliente."""
    # Primeiro confiro se o cliente existe. Se eu não checar aqui, a FK do banco
    # reclama e o usuário leva um 500 feio; assim eu devolvo um 404 que explica.
    if client_repo.get_by_id(data.client_id) is None:
        raise NotFoundError(f"Cliente {data.client_id} não encontrado")

    # Cada cliente só pode ter uma anamnese (relação 1:1). O banco já barra pelo
    # UNIQUE, mas checando antes eu consigo devolver um 409 com mensagem amigável.
    if repo.get_by_client_id(data.client_id) is not None:
        raise ConflictError(f"O cliente {data.client_id} já possui uma anamnese")

    return repo.create(data)


def get_all() -> list[Anamnesis]:
    """Lista todas as anamneses."""
    return repo.get_all()


def get_by_id(anamnesis_id: UUID) -> Optional[Anamnesis]:
    """Busca uma anamnese pelo ID. Devolve None se não achar."""
    return repo.get_by_id(anamnesis_id)


def update(anamnesis_id: UUID, data: AnamnesisUpdate) -> Optional[Anamnesis]:
    """Atualiza uma anamnese que já existe."""
    # exclude_none=True manda pro banco só o que veio preenchido, então dá pra
    # mudar um campo só sem zerar o resto. mode="json" deixa os tipos (UUID,
    # datetime) no formato que o Supabase aceita.
    update_data = data.model_dump(mode="json", exclude_none=True)

    # Corpo vazio é erro de quem chamou, não nosso. Esse ValueError vira um
    # HTTP 400 lá no main.py (tem um handler que cuida disso).
    if not update_data:
        raise ValueError("Nenhum campo para atualizar")

    # Se o PUT mandar is_active=true, aproveito pra "ressuscitar" o registro
    # limpando o deleted_at. É o contrário do que o DELETE faz (soft-delete).
    if update_data.get("is_active") is True:
        update_data["deleted_at"] = None

    return repo.update(anamnesis_id, update_data)


def delete(anamnesis_id: UUID) -> bool:
    """Remove a anamnese (soft-delete). True se removeu, False se o ID não existia."""
    return repo.delete(anamnesis_id)
