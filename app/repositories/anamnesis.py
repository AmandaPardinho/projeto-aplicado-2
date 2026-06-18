"""
Repositório da Anamnesis.
Esta é a única camada que conversa com o Supabase — todo acesso ao banco da
anamnese passa por aqui. Assim, se um dia trocarmos de banco, mexemos só neste arquivo.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from supabase import create_client, Client as SupabaseClient

from app.core.config import SUPABASE_URL, SUPABASE_KEY
from app.schemas.anamnesis import Anamnesis, AnamnesisCreate

# Conexão com o Supabase. Uso a chave service_role (de admin): como o backend
# roda no servidor, ele pode passar por cima do RLS sem perigo.
_client: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE = "anamnesis"


def create(data: AnamnesisCreate) -> Anamnesis:
    """Insere uma anamnese nova e devolve ela já criada."""
    # mode="json" converte os tipos do Python (UUID, datetime) pra texto que o
    # Supabase entende.
    response = _client.table(TABLE).insert(data.model_dump(mode="json")).execute()
    return Anamnesis.model_validate(response.data[0])


def get_all() -> list[Anamnesis]:
    """Devolve todas as anamneses cadastradas."""
    response = _client.table(TABLE).select("*").execute()
    return [Anamnesis.model_validate(row) for row in response.data]


def get_by_id(anamnesis_id: UUID) -> Optional[Anamnesis]:
    """Devolve a anamnese com aquele ID, ou None se não existir."""
    response = (
        _client.table(TABLE)
        .select("*")
        .eq("id", str(anamnesis_id))
        .execute()
    )
    if not response.data:
        return None
    return Anamnesis.model_validate(response.data[0])


def get_by_client_id(client_id: UUID) -> Optional[Anamnesis]:
    """Devolve a anamnese de um cliente, ou None se ele ainda não tem uma.

    É isso que garante o 1:1: o service usa essa busca pra não deixar criar uma
    segunda anamnese pro mesmo cliente (o banco também barra, com o UNIQUE).
    """
    response = (
        _client.table(TABLE)
        .select("*")
        .eq("client_id", str(client_id))
        .execute()
    )
    if not response.data:
        return None
    return Anamnesis.model_validate(response.data[0])


def get_active_client_ids() -> set[str]:
    """Devolve o conjunto de client_ids que têm uma anamnese ATIVA.

    Numa query só (em vez de uma por matrícula) — é o que o service usa pra
    marcar "anamnese pendente" na listagem sem cair no problema N+1.
    """
    response = (
        _client.table(TABLE)
        .select("client_id")
        .eq("is_active", True)
        .execute()
    )
    return {row["client_id"] for row in response.data}


def update(anamnesis_id: UUID, data: dict) -> Optional[Anamnesis]:
    """Atualiza uma anamnese e devolve ela já atualizada, ou None se não existir."""
    response = (
        _client.table(TABLE)
        .update(data)
        .eq("id", str(anamnesis_id))
        .execute()
    )
    if not response.data:
        return None
    return Anamnesis.model_validate(response.data[0])


def delete(anamnesis_id: UUID) -> bool:
    """"Apaga" a anamnese sem apagar de verdade (soft-delete).

    Em vez de remover a linha, marco is_active=False e guardo a hora em
    deleted_at. Assim mantenho o histórico (importante pra LGPD e auditoria).
    Devolve True se achou e atualizou, False se o ID não existia.
    """
    response = (
        _client.table(TABLE)
        .update({
            "is_active": False,
            "deleted_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", str(anamnesis_id))
        .execute()
    )
    return len(response.data) > 0
