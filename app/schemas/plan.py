"""
Plano (plan): os "pacotes" que o studio vende, tipo "8 sessões por mês".

Aqui ficam os modelos do Pydantic pro plano. O Pydantic olha as anotações de
tipo e já valida os dados sozinho pra gente.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


# 1) Entidade: o plano do jeito que está salvo no banco
# ===================================================================

class Plan(BaseModel):
    """Um plano como ele vive na tabela `plan` (uma linha do banco)."""
    id: UUID
    name: str
    sessions_per_month: int
    # Dinheiro a gente guarda como Decimal, não float: float arredonda errado
    # (199.90 vira 199.8999...). Decimal mantém os centavos certos.
    monthly_fee: Decimal
    is_active: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 2) O que chega no POST pra criar um plano
# ===================================================================

class PlanCreate(BaseModel):
    """Campos que o usuário manda no POST /plans pra cadastrar um plano."""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do plano")
    sessions_per_month: int = Field(..., gt=0, description="Quantidade de sessões por mês")
    monthly_fee: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, description="Mensalidade do plano")

# 3) O que devolvemos nos GETs
# ===================================================================

class PlanRead(Plan):
    """O que sai nos GETs. Deixo separado da entidade só pra não misturar
    o que entra (escrita) com o que sai (leitura)."""
    pass

# 4) O que chega no PUT pra editar um plano
# ===================================================================

class PlanUpdate(BaseModel):
    """Campos do PUT /plans/{id}. Tudo opcional: manda só o que quer mudar."""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nome do plano")
    sessions_per_month: Optional[int] = Field(None, gt=0, description="Quantidade de sessões por mês")
    monthly_fee: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2, description="Mensalidade do plano")
    is_active: Optional[bool] = None
