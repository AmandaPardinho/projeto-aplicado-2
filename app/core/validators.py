"""
Validators reutilizáveis para DTOs Pydantic.
Validação de FORMATO.
"""

import re
from datetime import date
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


# ===================================================================
# Data de nascimento
# ===================================================================

# Idade mínima para se matricular no studio (regra de negócio).
MIN_AGE_YEARS = 4


def validate_birth_date(v: Optional[date]) -> Optional[date]:
    """
    Valida a data de nascimento do cliente.
    - Não pode ser uma data no futuro.
    - O cliente deve ter no mínimo MIN_AGE_YEARS anos completos.
    - Recebe um objeto `date` (o Pydantic já converteu a string antes daqui).
    """
    if v is None:
        return v

    today = date.today()

    if v > today:
        raise ValueError("birth_date não pode ser uma data futura")

    # Idade completa: diferença de anos, menos 1 se ainda não fez aniversário este ano.
    # O par (mês, dia) compara as datas dentro do ano sem precisar de biblioteca extra.
    age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

    if age < MIN_AGE_YEARS:
        raise ValueError(
            f"cliente deve ter no mínimo {MIN_AGE_YEARS} anos de idade"
        )

    return v


# ===================================================================
# CREFITO (registro profissional do instrutor)
# ===================================================================

def validate_crefito(v: Optional[str]) -> Optional[str]:
    """
    Valida o formato do registro CREFITO do instrutor.
    - Aceita com prefixo opcional (CREFITO-10/) ou só o número.
    - Aceita 3 a 7 dígitos, com sufixo de letra opcional (ex.: 12345-F).
    - Retorna o valor normalizado (sem espaços, MAIÚSCULAS).
    """
    if v is None:
        return v

    normalized = v.strip().upper()
    pattern = r"^(CREFITO-\d+/)?\d{3,7}-?[A-Z]?$"
    if not re.match(pattern, normalized):
        raise ValueError("Formato inválido de CREFITO. Exemplo: 12345-F")
    return normalized
