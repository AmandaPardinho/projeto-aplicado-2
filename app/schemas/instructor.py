"""
Entidade Instructor.
DTOs (Data Transfer Objects) da entidade Instructor.
Validação declarativa via Pydantic.
"""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator

# ===================================================================
# 1. ENTIDADE — representa o registro do banco (espelha a tabela)
# ===================================================================

class Instructor(BaseModel):
    id: UUID
    name: str
    has_credential: bool
    credential_number: Optional[str]
    specialty: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===================================================================
# 2. DTO usado no POST /instructors
# ===================================================================

class InstructorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nome do instrutor")
    has_credential: bool = False
    credential_number: Optional[str] = None
    specialty: Optional[str] = Field(None, max_length=100)
    
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
    pass
