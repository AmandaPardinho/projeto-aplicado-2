"""
Cliente (client): o aluno do studio.

Aqui ficam os modelos do Pydantic pro cliente. O Pydantic valida o que chega
usando os validators de CPF, WhatsApp e data de nascimento.
"""

import re
from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from enum import Enum

from app.core.validators import (
    validate_cpf,
    validate_whatsapp_br,
    validate_birth_date,
    validate_date_year,
    validate_person_name,
    normalize_email_lower,
)



class ClientStatus(str, Enum):
    """Em que ponto o cliente está com a gente comercialmente (bate com o CHECK do banco)."""
    PROSPECT = "prospect"
    ACTIVE = "active"
    INACTIVE = "inactive"

# 1) Entidade: o cliente do jeito que está salvo no banco
# ===================================================================

class Client(BaseModel):
    """Um cliente como ele vive na tabela `client` (uma linha do banco)."""
    id: UUID
    name: str
    whatsapp_number: str
    cpf: str
    email: EmailStr
    birth_date: date
    marketing_consent: bool
    client_status: ClientStatus
    is_active: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 2) O que chega no POST pra cadastrar um cliente
# ===================================================================

class ClientCreate(BaseModel):
    """Campos que o usuário manda no POST /clients pra cadastrar um aluno."""
    name: str = Field(..., max_length=100, description="Nome do cliente")
    whatsapp_number: str = Field(..., description="Número do Whatsapp do cliente")
    cpf: str = Field(..., description="Número do CPF do cliente")
    email: EmailStr = Field(..., description="E-mail do cliente (do responsável, no caso de menores)")
    birth_date: date
    marketing_consent: bool = True
    client_status: ClientStatus = ClientStatus.PROSPECT
    _normalize_name = field_validator("name", mode="before")(validate_person_name)
    _normalize_email = field_validator("email", mode="before")(normalize_email_lower)
    _normalize_cpf = field_validator("cpf", mode="before")(validate_cpf)
    _normalize_whatsapp = field_validator("whatsapp_number", mode="before")(validate_whatsapp_br)
    _check_birth_year = field_validator("birth_date", mode="before")(validate_date_year)
    _validate_birth_date = field_validator("birth_date")(validate_birth_date)

# 3) O que devolvemos nos GETs
# ===================================================================

class ClientRead(Client):
    """O que sai nos GETs. Separado da entidade só pra não misturar leitura e escrita."""
    pass

# 4) O que chega no PUT pra editar um cliente
# ===================================================================

class ClientUpdate(BaseModel):
    """Campos do PUT /clients/{id}. Tudo opcional: manda só o que mudou.

    cpf e birth_date não entram aqui de propósito: são dados de registro civil,
    não mudam na vida real. Eles só existem no ClientCreate. Se alguém mandar um
    deles num PUT, o Pydantic simplesmente ignora (vira campo extra).
    """
    name: Optional[str] = Field(None, max_length=100, description="Nome do cliente")
    whatsapp_number: Optional[str] = Field(None, description="Número do Whatsapp do cliente")
    email: Optional[EmailStr] = Field(None, description="E-mail do cliente")
    marketing_consent: Optional[bool] = None
    client_status: Optional[ClientStatus] = None
    is_active: Optional[bool] = None
    _normalize_name = field_validator("name", mode="before")(validate_person_name)
    _normalize_email = field_validator("email", mode="before")(normalize_email_lower)
    _normalize_whatsapp = field_validator("whatsapp_number", mode="before")(validate_whatsapp_br)
