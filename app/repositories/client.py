"""
Repositório do Cliente.
Esta é a única camada que conversa com o Supabase — todo acesso ao banco do
cliente passa por aqui. Assim, se um dia trocarmos de banco, mexemos só neste arquivo.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from supabase import create_client, Client as SupabaseClient

from app.core.config import SUPABASE_URL, SUPABASE_KEY
from app.schemas.client import Client, ClientCreate

# Conexão com o Supabase. Uso a chave service_role (de admin): como o backend
# roda no servidor, ele pode passar por cima do RLS sem perigo.
_client: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE = "client"


def create(data: ClientCreate) -> Client:
    """Insere um cliente novo e devolve ele já criado."""
    # mode="json" converte os tipos do Python (date, datetime, UUID, Enum) pra
    # texto que o Supabase entende.
    response = _client.table(TABLE).insert(data.model_dump(mode="json")).execute()
    return Client.model_validate(response.data[0])


def get_all() -> list[Client]:
    """Devolve todos os clientes cadastrados."""
    response = _client.table(TABLE).select("*").execute()
    return [Client.model_validate(row) for row in response.data]


def get_by_id(client_id: UUID) -> Optional[Client]:
    """Devolve o cliente com aquele ID, ou None se não existir."""
    response = (
        _client.table(TABLE)
        .select("*")
        .eq("id", str(client_id))
        .execute()
    )
    if not response.data:
        return None
    return Client.model_validate(response.data[0])


def get_by_cpf(cpf: str) -> Optional[Client]:
    """Devolve o cliente que tem aquele CPF, ou None.

    Olho TODAS as linhas, inclusive as soft-deletadas: igual ao UNIQUE do banco,
    um CPF de cliente desativado continua "ocupado".
    """
    response = (
        _client.table(TABLE)
        .select("*")
        .eq("cpf", cpf)
        .execute()
    )
    if not response.data:
        return None
    return Client.model_validate(response.data[0])


def update(client_id: UUID, data: dict) -> Optional[Client]:
    """Atualiza um cliente e devolve ele já atualizado, ou None se não existir."""
    response = (
        _client.table(TABLE)
        .update(data)
        .eq("id", str(client_id))
        .execute()
    )
    if not response.data:
        return None
    return Client.model_validate(response.data[0])


def delete(client_id: UUID) -> bool:
    """"Apaga" o cliente sem apagar de verdade (soft-delete).

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
        .eq("id", str(client_id))
        .execute()
    )
    return len(response.data) > 0
