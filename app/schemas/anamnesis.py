"""
Anamnese (anamnesis): a ficha de saúde que o cliente preenche antes de começar.

São aquelas perguntas de "tem alguma doença? toma remédio? tem restrição?".
Aqui ficam os modelos do Pydantic pra essa ficha.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


# 1) Entidade: a anamnese do jeito que está salva no banco
# ===================================================================

class Anamnesis(BaseModel):
    """Uma anamnese como ela vive na tabela `anamnesis` (uma linha do banco)."""
    id: UUID
    client_id: UUID
    previous_illness: bool
    illness_description: Optional[str] = None
    specific_complaint: bool
    complaint_description: Optional[str] = None
    medication_use: bool
    medication_description: Optional[str] = None
    physical_restriction: bool
    restriction_description: Optional[str] = None
    cleared_for_activity: bool
    filled_at: datetime
    is_active: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 2) O que chega no POST pra criar uma anamnese
# ===================================================================

class AnamnesisCreate(BaseModel):
    """Campos que o usuário manda no POST /anamneses.

    Não peço o filled_at aqui: quem preenche é o banco, com a hora do INSERT.
    """
    client_id: UUID = Field(..., description="ID do cliente dono da anamnese")
    previous_illness: bool = Field(False, description="Possui doença prévia?")
    illness_description: Optional[str] = Field(None, description="Descrição da doença prévia")
    specific_complaint: bool = Field(False, description="Possui queixa específica?")
    complaint_description: Optional[str] = Field(None, description="Descrição da queixa")
    medication_use: bool = Field(False, description="Faz uso de medicação?")
    medication_description: Optional[str] = Field(None, description="Descrição da medicação")
    physical_restriction: bool = Field(False, description="Possui restrição física?")
    restriction_description: Optional[str] = Field(None, description="Descrição da restrição")
    cleared_for_activity: bool = Field(False, description="Liberado para atividade física?")

    @model_validator(mode="after")
    def validate_description_pairs(self):
        """Mantém cada par flag↔descrição coerente nos dois sentidos.

        - Marcou "sim"? A descrição vira obrigatória (não dá pra dizer que tem
          uma doença e não descrever qual).
        - Marcou "não"? A descrição não pode vir preenchida (descrição órfã numa
          resposta "não" é contradição — o checkbox diz uma coisa, o texto outra).
        É a mesma ideia do has_credential/credential_number do instrutor.
        """
        pairs = [
            ("previous_illness", "illness_description"),
            ("specific_complaint", "complaint_description"),
            ("medication_use", "medication_description"),
            ("physical_restriction", "restriction_description"),
        ]
        for flag, description in pairs:
            flag_on = getattr(self, flag)
            has_text = bool(getattr(self, description))
            if flag_on and not has_text:
                raise ValueError(f"{description} é obrigatório quando {flag}=True")
            if not flag_on and has_text:
                raise ValueError(f"{description} não deve ser preenchido quando {flag}=False")
        return self

# 3) O que devolvemos nos GETs
# ===================================================================

class AnamnesisRead(Anamnesis):
    """O que sai nos GETs. Separado da entidade só pra não misturar leitura e escrita."""
    pass

# 4) O que chega no PUT pra editar uma anamnese
# ===================================================================

class AnamnesisUpdate(BaseModel):
    """Campos do PUT /anamneses/{id}. Tudo opcional: manda só o que mudou.

    client_id e filled_at ficam de fora de propósito: a anamnese não troca de
    dono e a data original de preenchimento não se mexe. A regra "marcou sim ->
    descreve" também não roda aqui: num update parcial a descrição pode já estar
    salva no banco e não vir no que o usuário mandou.
    """
    previous_illness: Optional[bool] = None
    illness_description: Optional[str] = None
    specific_complaint: Optional[bool] = None
    complaint_description: Optional[str] = None
    medication_use: Optional[bool] = None
    medication_description: Optional[str] = None
    physical_restriction: Optional[bool] = None
    restriction_description: Optional[str] = None
    cleared_for_activity: Optional[bool] = None
    is_active: Optional[bool] = None
