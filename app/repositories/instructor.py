"""
Repositório do Instructor.
Única camada que fala com o Supabase. Encapsula todo acesso ao banco.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from supabase import create_client, Client

from app.core.config import SUPABASE_URL, SUPABASE_ANON_KEY
from app.schemas.instructor import Instructor, InstructorCreate

# Cliente Supabase compartilhado 
_client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
TABLE = "instructor"


def create(data: InstructorCreate) -> Instructor:
    """Insere novo instrutor e retorna a entidade criada."""
    # mode="json" serializa date/datetime/UUID/Enum em strings JSON-compatíveis
    response = _client.table(TABLE).insert(data.model_dump(mode="json")).execute()
    return Instructor.model_validate(response.data[0])


def get_all() -> list[Instructor]:
    """Retorna todos os instrutores cadastrados."""
    response = _client.table(TABLE).select("*").execute()
    return [Instructor.model_validate(row) for row in response.data]


def get_by_id(instructor_id: UUID) -> Optional[Instructor]:
    """Retorna o instrutor com o ID informado, ou None se não existir."""
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
    """Atualiza um instrutor. Retorna a entidade atualizada ou None se não existir."""
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
    """
    Soft-delete: marca is_active=False e registra o momento em deleted_at.
    NÃO remove a linha do banco (LGPD compliance + auditoria).
    Retorna True se a operação afetou alguma linha, False se o ID não existia.
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
