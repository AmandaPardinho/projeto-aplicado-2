"""
Repositório do Instructor.
Esta é a única camada que conversa com o Supabase — todo acesso ao banco do
instrutor passa por aqui. Assim, se um dia trocarmos de banco, mexemos só neste arquivo.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from supabase import create_client, Client

from app.core.config import SUPABASE_URL, SUPABASE_KEY
from app.schemas.instructor import Instructor, InstructorCreate

# Conexão com o Supabase. Uso a chave service_role (de admin): como o backend
# roda no servidor, ele pode passar por cima do RLS sem perigo.
_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE = "instructor"


def create(data: InstructorCreate) -> Instructor:
    """Insere um instrutor novo e devolve ele já criado."""
    # mode="json" converte os tipos do Python (date, datetime, UUID, Enum) pra
    # texto que o Supabase entende.
    response = _client.table(TABLE).insert(data.model_dump(mode="json")).execute()
    return Instructor.model_validate(response.data[0])


def get_all() -> list[Instructor]:
    """Devolve todos os instrutores cadastrados."""
    response = _client.table(TABLE).select("*").execute()
    return [Instructor.model_validate(row) for row in response.data]


def get_by_id(instructor_id: UUID) -> Optional[Instructor]:
    """Devolve o instrutor com aquele ID, ou None se não existir."""
    response = (
        _client.table(TABLE)
        .select("*")
        .eq("id", str(instructor_id))
        .execute()
    )
    if not response.data:
        return None
    return Instructor.model_validate(response.data[0])


def update(instructor_id: UUID, data: dict) -> Optional[Instructor]:
    """Atualiza um instrutor e devolve ele já atualizado, ou None se não existir."""
    response = (
        _client.table(TABLE)
        .update(data)
        .eq("id", str(instructor_id))
        .execute()
    )
    if not response.data:
        return None
    return Instructor.model_validate(response.data[0])


def delete(instructor_id: UUID) -> bool:
    """"Apaga" o instrutor sem apagar de verdade (soft-delete).

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
        .eq("id", str(instructor_id))
        .execute()
    )
    return len(response.data) > 0
