"""
Entidade Instructor.
DTOs (Data Transfer Objects) da entidade Instructor.
Validação declarativa via Pydantic.
"""

import re
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator


class InstructorStatus(str, Enum):
    """Situação contratual do instrutor (espelha o CHECK do banco)."""
    ATIVO = "ativo"
    FERIAS = "ferias"
    AFASTADO = "afastado"
    BANCO_DE_VAGAS = "banco_de_vagas"
    INATIVO = "inativo"


# ===================================================================
# 1. ENTIDADE — representa o registro do banco (espelha a tabela)
# ===================================================================

class Instructor(BaseModel):
    """Entidade Instructor — espelha 1:1 o registro da tabela `instructor` no banco."""
    id: UUID
    name: str
    has_credential: bool
    credential_number: Optional[str] = None
    specialty: Optional[str] = None
    instructor_status: InstructorStatus
    is_active: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===================================================================
# 2. DTO usado no POST /instructors
# ===================================================================

class InstructorCreate(BaseModel):
    """DTO de entrada do POST /instructors — campos que o usuário envia ao cadastrar."""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do instrutor")
    has_credential: bool = False
    credential_number: Optional[str] = None
    specialty: Optional[str] = Field(None, max_length=100)
    instructor_status: InstructorStatus = InstructorStatus.ATIVO
    
    @field_validator("credential_number")
    @classmethod
    def validate_credential_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        pattern = r"^(CREFITO-\d+/)?\d{3,7}-?[A-Z]?$"
        if not re.match(pattern, v.strip().upper()):
            raise ValueError("Formato inválido de CREFITO. Exemplo: 12345-F")
        return v.strip().upper()
    
    @model_validator(mode="after")
    def validate_credential_consistency(self):
        """
        Garante coerência entre has_credential e credential_number.
        Regra: se has_credential=True, credential_number é obrigatório.
        """
        if self.has_credential and not self.credential_number:
            raise ValueError("credential_number é obrigatório quando has_credential=True")
        return self

# ===================================================================
# 3. DTO usado no GET /instructors
# ===================================================================

class InstructorRead(Instructor):
    """DTO de saída dos GETs — herda de Instructor. Existe para desacoplar leitura de escrita."""
    pass

# ===================================================================
# 4. DTO usado no UPDATE /instructors/{id}
# ===================================================================

class InstructorUpdate(BaseModel):
    """DTO de atualização — todos os campos opcionais (partial update)."""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nome do instrutor")
    has_credential: Optional[bool] = None
    credential_number: Optional[str] = None
    specialty: Optional[str] = Field(None, max_length=100)
    instructor_status: Optional[InstructorStatus] = None
    is_active: Optional[bool] = None
    
    @field_validator("credential_number")
    @classmethod
    def validate_credential_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        pattern = r"^(CREFITO-\d+/)?\d{3,7}-?[A-Z]?$"
        if not re.match(pattern, v.strip().upper()):
            raise ValueError("Formato inválido de CREFITO. Exemplo: 12345-F")
        return v.strip().upper()
    
