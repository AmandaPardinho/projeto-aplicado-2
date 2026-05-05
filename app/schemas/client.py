"""
Entidade Cliente.
DTOs (Data Transfer Objects) da entidade Cliente.
Validação declarativa via Pydantic.
"""

import re
from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum

from app.core.validators import validate_cpf, validate_whatsapp_br



class ClientStatus(str, Enum):
    """Estágio do relacionamento comercial com o cliente (espelha o CHECK do banco)."""
    PROSPECTO = "prospecto"
    ATIVO = "ativo"
    INATIVO = "inativo"

# ===================================================================
# 1. ENTIDADE — representa o registro do banco (espelha a tabela)
# ===================================================================

class Client(BaseModel):
    """Entidade Cliente — espelha 1:1 o registro da tabela `client` no banco."""
    id: UUID
    name: str
    whatsapp_number: str
    cpf: str
    birth_date: date
    marketing_consent: bool
    client_status: ClientStatus
    is_active: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===================================================================
# 2. DTO usado no POST /client
# ===================================================================

class ClientCreate(BaseModel):
    """DTO de entrada do POST /clients — campos que o usuário envia ao cadastrar."""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do cliente")
    whatsapp_number: str = Field(..., description="Número do Whatsapp do cliente")
    cpf: str = Field(..., description="Número do CPF do cliente")
    birth_date: date
    marketing_consent: bool = True
    client_status: ClientStatus = ClientStatus.PROSPECTO
    _normalize_cpf = field_validator("cpf", mode="before")(validate_cpf)
    _normalize_whatsapp = field_validator("whatsapp_number", mode="before")(validate_whatsapp_br)

# ===================================================================
# 3. DTO usado no GET /client
# ===================================================================

class ClientRead(Client):
    """DTO de saída dos GETs — herda de Client. Existe para desacoplar leitura de escrita."""
    pass

# ===================================================================
# 4. DTO usado no UPDATE /client/{id}
# ===================================================================

class ClientUpdate(BaseModel):
    """DTO de atualização — todos os campos opcionais (partial update)."""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nome do cliente")
    whatsapp_number: Optional[str] = Field(None, description="Número do Whatsapp do cliente")
    cpf: Optional[str] = Field(None, description="Número do CPF do cliente")
    birth_date: Optional[date] = None
    marketing_consent: Optional[bool] = None
    client_status: Optional[ClientStatus] = None
    is_active: Optional[bool] = None
    _normalize_cpf = field_validator("cpf", mode="before")(validate_cpf)
    _normalize_whatsapp = field_validator("whatsapp_number", mode="before")(validate_whatsapp_br)
    