"""
Validators reutilizáveis para DTOs Pydantic.
Validação de FORMATO.
"""

import re
from typing import Optional


def _only_digits(value: str) -> str:
    """Remove tudo que não for dígito."""
    return re.sub(r"\D", "", value)


# ===================================================================
# CPF
# ===================================================================

def validate_cpf(v: Optional[str]) -> Optional[str]:
    """
    Valida CPF brasileiro.
    - Aceita com máscara (000.000.000-00) ou sem (00000000000).
    - Verifica os 2 dígitos verificadores (algoritmo oficial da Receita).
    - Rejeita CPFs com todos os dígitos iguais (11111111111 etc.).
    - Retorna o CPF normalizado (só os 11 dígitos).
    """
    if v is None:
        return v
    if not isinstance(v, str):
        raise ValueError("cpf deve ser string")

    digits = _only_digits(v)

    if len(digits) != 11:
        raise ValueError("CPF deve conter 11 dígitos")

    # Rejeita sequências repetidas
    if len(set(digits)) == 1:
        raise ValueError("CPF inválido")

    # Cálculo do 1º dígito verificador
    soma = sum(int(digits[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto
    if dv1 != int(digits[9]):
        raise ValueError("CPF inválido (dígito verificador)")

    # Cálculo do 2º dígito verificador
    soma = sum(int(digits[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto
    if dv2 != int(digits[10]):
        raise ValueError("CPF inválido (dígito verificador)")

    return digits  


# ===================================================================
# WhatsApp (número brasileiro)
# ===================================================================

def validate_whatsapp_br(v: Optional[str]) -> Optional[str]:
    """
    Valida número de WhatsApp brasileiro.
    - Aceita com ou sem código do país (+55).
    - Aceita máscara: (11) 98765-4321, +55 11 98765-4321, 11987654321 etc.
    - Exige celular (deve ter o 9 após o DDD).
    - Retorna formato sem o '+': '5511987654321'.
    """
    if v is None:
        return v
    if not isinstance(v, str):
        raise ValueError("whatsapp_number deve ser string")

    digits = _only_digits(v)

    # Normaliza: se vier sem o 55, adiciona
    if len(digits) == 11:
        digits = "55" + digits
    elif len(digits) != 13:
        raise ValueError(
            "whatsapp_number deve ter 11 dígitos (DDD + celular) "
            "ou 13 com código do país"
        )

    if not digits.startswith("55"):
        raise ValueError("whatsapp_number deve ser brasileiro (código 55)")

    ddd = int(digits[2:4])
    if ddd < 11 or ddd > 99:
        raise ValueError(f"DDD {ddd} inválido")

    # Celular brasileiro: nono dígito obrigatório (9 após o DDD)
    if digits[4] != "9":
        raise ValueError(
            "whatsapp_number deve ser celular (deve começar com 9 após o DDD)"
        )

    return digits
