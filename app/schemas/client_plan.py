"""
Matrícula (client_plan): liga uma aluna a um plano — é a "assinatura" dela.

Entidade de junção entre client e plan, mas com dados próprios da matrícula
(início, vencimento, renovação). Aqui ficam os modelos Pydantic.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from app.core.validators import validate_date_year


# 1) Entidade: a matrícula do jeito que está salva no banco
# ===================================================================

class ClientPlan(BaseModel):
    """Uma matrícula como ela vive na tabela `client_plan` (uma linha do banco)."""
    id: UUID
    client_id: UUID
    plan_id: UUID
    start_date: date
    end_date: date
    renewal_date: Optional[date] = None
    is_active: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 2) O que chega no POST pra criar uma matrícula
# ===================================================================

class ClientPlanCreate(BaseModel):
    """Campos que o usuário manda no POST /client_plans.

    end_date NÃO entra aqui: a matrícula vale 1 ano, então o service calcula
    end_date = start_date + 1 ano. start_date é opcional (default: hoje).
    renewal_date é manual: fica vazio na 1ª matrícula e recebe a data da
    rematrícula quando a aluna já fazia antes.
    """
    client_id: UUID = Field(..., description="ID da aluna dona da matrícula")
    plan_id: UUID = Field(..., description="ID do plano contratado")
    start_date: Optional[date] = Field(None, description="Início da matrícula (default: hoje)")
    renewal_date: Optional[date] = Field(None, description="Data da rematrícula (vazio na 1ª vez)")
    _check_start_year = field_validator("start_date", mode="before")(validate_date_year)
    _check_renewal_year = field_validator("renewal_date", mode="before")(validate_date_year)


# 3) O que devolvemos nos GETs
# ===================================================================

class ClientPlanRead(ClientPlan):
    """O que sai nos GETs.

    Além das colunas do banco, carrega `anamnesis_pending`: um campo DERIVADO
    (não existe na tabela) que o service calcula — True quando a aluna não tem
    anamnese ativa. É a flag que o front mostra como "anamnese pendente".
    """
    anamnesis_pending: bool = Field(
        False,
        description="True se a aluna não tem anamnese ativa (ficha de saúde pendente).",
    )


# 4) O que chega no PUT pra editar uma matrícula
# ===================================================================

class ClientPlanUpdate(BaseModel):
    """Campos do PUT /client_plans/{id}. Tudo opcional: manda só o que mudou.

    start_date e end_date ficam de fora: o início é imutável (trigger no banco)
    e o vencimento é derivado dele. Trocar de plano é uma matrícula NOVA, não um
    update — por isso plan_id também não entra aqui.
    """
    renewal_date: Optional[date] = None
    is_active: Optional[bool] = None
    _check_renewal_year = field_validator("renewal_date", mode="before")(validate_date_year)
