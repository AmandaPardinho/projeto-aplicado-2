"""
Repositório da Matrícula (client_plan).
Única camada que conversa com o Supabase pra essa entidade.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from supabase import create_client, Client as SupabaseClient

from app.core.config import SUPABASE_URL, SUPABASE_KEY
from app.schemas.client_plan import ClientPlan

# Conexão com o Supabase (service_role: o backend roda no servidor e passa por
# cima do RLS sem perigo).
_client: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE = "client_plan"


def create(payload: dict) -> ClientPlan:
    """Insere uma matrícula nova e devolve ela já criada.

    Recebe um dict (e não o schema Create) porque o service monta o payload com
    campos derivados — o end_date calculado e o start_date com default de hoje.
    """
    response = _client.table(TABLE).insert(payload).execute()
    return ClientPlan.model_validate(response.data[0])


def get_all() -> list[ClientPlan]:
    """Devolve todas as matrículas cadastradas."""
    response = _client.table(TABLE).select("*").execute()
    return [ClientPlan.model_validate(row) for row in response.data]


def get_by_id(client_plan_id: UUID) -> Optional[ClientPlan]:
    """Devolve a matrícula com aquele ID, ou None se não existir."""
    response = _client.table(TABLE).select("*").eq("id", str(client_plan_id)).execute()
    if not response.data:
        return None
    return ClientPlan.model_validate(response.data[0])


def get_active_by_client_id(client_id: UUID) -> Optional[ClientPlan]:
    """Devolve a matrícula ATIVA da aluna, ou None.

    É o que sustenta a regra "1 aluna -> 1 plano ativo": o service usa essa busca
    pra barrar uma segunda matrícula ativa (o banco também barra, com o índice
    único parcial em client_id WHERE is_active).
    """
    response = (
        _client.table(TABLE)
        .select("*")
        .eq("client_id", str(client_id))
        .eq("is_active", True)
        .execute()
    )
    if not response.data:
        return None
    return ClientPlan.model_validate(response.data[0])


def update(client_plan_id: UUID, data: dict) -> Optional[ClientPlan]:
    """Atualiza uma matrícula e devolve ela já atualizada, ou None se não existir."""
    response = _client.table(TABLE).update(data).eq("id", str(client_plan_id)).execute()
    if not response.data:
        return None
    return ClientPlan.model_validate(response.data[0])


def delete(client_plan_id: UUID) -> bool:
    """Soft-delete: marca is_active=False e grava deleted_at. True se achou e atualizou."""
    response = (
        _client.table(TABLE)
        .update({
            "is_active": False,
            "deleted_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", str(client_plan_id))
        .execute()
    )
    return len(response.data) > 0
