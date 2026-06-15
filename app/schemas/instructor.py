"""
Instrutor (instructor): quem dá as aulas no studio.

Nem todo instrutor é fisioterapeuta com registro no conselho (CREFITO), então a
credencial é opcional. Aqui ficam os modelos do Pydantic pro instrutor.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.validators import validate_crefito


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
    name: str = Field(..., min_length=2, max_length=100, description="Nome do instrutor")
    email: EmailStr = Field(..., description="E-mail do instrutor")
    has_credential: bool = False
    credential_number: Optional[str] = None
    specialty: Optional[str] = Field(None, max_length=100)
    instructor_status: InstructorStatus = InstructorStatus.ACTIVE
    _validate_crefito = field_validator("credential_number")(validate_crefito)

    @model_validator(mode="after")
    def validate_credential_consistency(self):
        """Se marcou que tem credencial, o número vira obrigatório.

        Não dá pra dizer has_credential=True e deixar o credential_number vazio.
        """
        if self.has_credential and not self.credential_number:
            raise ValueError("credential_number é obrigatório quando has_credential=True")
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
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nome do instrutor")
    email: Optional[EmailStr] = Field(None, description="E-mail do instrutor")
    has_credential: Optional[bool] = None
    credential_number: Optional[str] = None
    specialty: Optional[str] = Field(None, max_length=100)
    instructor_status: Optional[InstructorStatus] = None
    is_active: Optional[bool] = None
    _validate_crefito = field_validator("credential_number")(validate_crefito)
