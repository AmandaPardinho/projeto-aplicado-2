"""
Instrutor (instructor): quem dá as aulas no studio.

O instrutor pode ser de qualquer área (educação física, fisioterapia, dança,
medicina...), com ou sem conselho de classe — por isso o registro profissional
é opcional e genérico, não preso ao CREFITO. Aqui ficam os modelos do Pydantic.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.validators import validate_credential, validate_person_name, normalize_email_lower


class InstructorStatus(str, Enum):
    """Situação do instrutor no studio (bate com o CHECK do banco)."""
    ACTIVE = "active"
    VACATION = "vacation"        # ferias
    ON_LEAVE = "on_leave"        # afastado
    STANDBY = "standby"          # banco_de_vagas
    INACTIVE = "inactive"


# 1) Entidade: o instrutor do jeito que está salvo no banco
# ===================================================================

class Instructor(BaseModel):
    """Um instrutor como ele vive na tabela `instructor` (uma linha do banco)."""
    id: UUID
    name: str
    email: EmailStr
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

# 2) O que chega no POST pra cadastrar um instrutor
# ===================================================================

class InstructorCreate(BaseModel):
    """Campos que o usuário manda no POST /instructors pra cadastrar um instrutor."""
    name: str = Field(..., max_length=100, description="Nome do instrutor")
    email: EmailStr = Field(..., description="E-mail do instrutor")
    has_credential: bool = False
    credential_number: Optional[str] = None
    specialty: Optional[str] = Field(None, max_length=100)
    instructor_status: InstructorStatus = InstructorStatus.ACTIVE
    _normalize_name = field_validator("name", mode="before")(validate_person_name)
    _normalize_email = field_validator("email", mode="before")(normalize_email_lower)
    _validate_credential = field_validator("credential_number")(validate_credential)

    @model_validator(mode="after")
    def validate_credential_consistency(self):
        """Mantém o par has_credential ↔ credential_number coerente nos dois sentidos.

        - Marcou que tem registro? Então o número é obrigatório.
        - Marcou que NÃO tem? Então não pode mandar um número órfão pendurado.
        """
        if self.has_credential and not self.credential_number:
            raise ValueError("credential_number é obrigatório quando has_credential=True")
        if not self.has_credential and self.credential_number:
            raise ValueError("credential_number não deve ser preenchido quando has_credential=False")
        return self

# 3) O que devolvemos nos GETs
# ===================================================================

class InstructorRead(Instructor):
    """O que sai nos GETs. Separado da entidade só pra não misturar leitura e escrita."""
    pass

# 4) O que chega no PUT pra editar um instrutor
# ===================================================================

class InstructorUpdate(BaseModel):
    """Campos do PUT /instructors/{id}. Tudo opcional: manda só o que mudou."""
    name: Optional[str] = Field(None, max_length=100, description="Nome do instrutor")
    email: Optional[EmailStr] = Field(None, description="E-mail do instrutor")
    has_credential: Optional[bool] = None
    credential_number: Optional[str] = None
    specialty: Optional[str] = Field(None, max_length=100)
    instructor_status: Optional[InstructorStatus] = None
    is_active: Optional[bool] = None
    _normalize_name = field_validator("name", mode="before")(validate_person_name)
    _normalize_email = field_validator("email", mode="before")(normalize_email_lower)
    _validate_credential = field_validator("credential_number")(validate_credential)
