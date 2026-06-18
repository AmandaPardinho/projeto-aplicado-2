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
# Nome
# ===================================================================

# Nome de PESSOA: letras (com acento), espaço, hífen e apóstrofo.
# Libera compostos reais ("Anne-Marie", "D'Ávila", "Zé do Ó") e barra
# número, emoji, <>, @ e qualquer símbolo. O range cobre os acentos do PT-BR.
_PERSON_NAME_RE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' \-]+$")
MIN_NAME_LETTERS = 3


def validate_person_name(v):
    """
    Valida e normaliza o nome de uma PESSOA (cliente/instrutor).

    Roda em modo `before`:
    - Tira espaços das pontas e colapsa espaços/tabs/quebras internas.
    - Exige no mínimo MIN_NAME_LETTERS letras.
    - Só aceita letras, espaço, hífen e apóstrofo (sem número/emoji/símbolo).
    - Mantém a CAIXA como foi digitada (a exibição em maiúsculo é só na tela,
      via CSS): assim não perdemos "João McDonald" virando "JOÃO MCDONALD".
    """
    if v is None:
        return v
    if not isinstance(v, str):
        raise ValueError("nome deve ser texto")

    cleaned = " ".join(v.split())
    if not cleaned:
        raise ValueError("nome não pode ficar em branco")
    if not _PERSON_NAME_RE.match(cleaned):
        raise ValueError("nome deve conter apenas letras, espaços, hífen e apóstrofo")
    letters = sum(1 for c in cleaned if c.isalpha())
    if letters < MIN_NAME_LETTERS:
        raise ValueError(f"nome deve ter no mínimo {MIN_NAME_LETTERS} letras")

    return cleaned


def normalize_name(v):
    """
    Normaliza um nome "solto" (ex.: nome de PLANO): trim e colapsa espaços,
    mantendo a caixa digitada. Não restringe caracteres — número e barra são ok
    ("8 sessões/mês"). Só não deixa ficar em branco.
    """
    if v is None:
        return v
    if not isinstance(v, str):
        raise ValueError("nome deve ser texto")

    cleaned = " ".join(v.split())
    if not cleaned:
        raise ValueError("nome não pode ficar em branco")

    return cleaned


# ===================================================================
# E-mail
# ===================================================================

def normalize_email_lower(v):
    """
    Padroniza o e-mail em minúsculo (e sem espaços nas pontas) antes de o
    Pydantic validar o formato. Evita tratar 'A@X.COM' e 'a@x.com' como
    pessoas diferentes.
    """
    if isinstance(v, str):
        return v.strip().lower()
    return v


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

# DDDs que realmente existem no Brasil (Plano Nacional de Numeração da Anatel).
# Vários números entre 11 e 99 NÃO são DDDs válidos (ex.: 23, 25, 30) — por isso
# usamos uma lista fechada em vez de só checar a faixa. Agrupados por região.
VALID_DDDS = frozenset({
    11, 12, 13, 14, 15, 16, 17, 18, 19,              # SP
    21, 22, 24, 27, 28,                              # RJ / ES
    31, 32, 33, 34, 35, 37, 38,                      # MG
    41, 42, 43, 44, 45, 46, 47, 48, 49,              # PR / SC
    51, 53, 54, 55,                                  # RS
    61, 62, 63, 64, 65, 66, 67, 68, 69,              # Centro-Oeste / AC / RO / TO
    71, 73, 74, 75, 77, 79,                          # BA / SE
    81, 82, 83, 84, 85, 86, 87, 88, 89,              # Nordeste
    91, 92, 93, 94, 95, 96, 97, 98, 99,              # Norte
})

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
    if ddd not in VALID_DDDS:
        raise ValueError(f"DDD {ddd:02d} inválido (não existe no Brasil)")

    # Celular brasileiro: nono dígito obrigatório (9 após o DDD)
    if digits[4] != "9":
        raise ValueError(
            "whatsapp_number deve ser celular (deve começar com 9 após o DDD)"
        )

    return digits


# ===================================================================
# Data de nascimento
# ===================================================================

# Faixa de idade aceita para se matricular no studio (regra de negócio).
MIN_AGE_YEARS = 4
MAX_AGE_YEARS = 120


def validate_birth_date(v: Optional[date]) -> Optional[date]:
    """
    Valida a data de nascimento do cliente.
    - Não pode ser uma data no futuro.
    - O cliente deve ter entre MIN_AGE_YEARS e MAX_AGE_YEARS anos completos.
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

    if age > MAX_AGE_YEARS:
        raise ValueError(
            f"cliente deve ter no máximo {MAX_AGE_YEARS} anos de idade"
        )

    return v


def validate_date_year(v):
    """
    Garante que o ano da data tem no máximo 4 dígitos.

    Roda em modo `before` (antes do Pydantic converter a string em `date`):
    se o usuário mandar "50525-01-01", troca o erro críptico do Pydantic por
    uma mensagem clara. Datas válidas passam intactas para a conversão normal.
    """
    if isinstance(v, str):
        # No formato ISO (YYYY-MM-DD) o ano é o bloco antes do primeiro '-'.
        year_part = v.strip().split("-")[0]
        if year_part.isdigit() and len(year_part) > 4:
            raise ValueError("o ano da data deve ter no máximo 4 dígitos")
    return v


# ===================================================================
# Registro profissional (credencial do instrutor)
# ===================================================================

# Genérico, não preso a um conselho só: o instrutor pode ser de educação física
# (CREF), fisioterapia (CREFITO), medicina (CRM) ou área sem conselho. O número é
# obrigatório; a letra de categoria (ex.: -G, -F) e a UF (/SP) são opcionais.
_CREDENTIAL_RE = re.compile(r"^\d{3,15}(-[A-Z])?(/[A-Z]{2})?$")


def validate_credential(v: Optional[str]) -> Optional[str]:
    """
    Valida o número de registro profissional do instrutor.
    - Exige de 3 a 15 dígitos (o número em si).
    - Aceita sufixo opcional de categoria (-G, -F...) e de UF (/SP).
    - Não força nenhum conselho específico (serve pra CREF, CREFITO, CRM etc.).
    - Retorna normalizado (sem espaços, MAIÚSCULAS).
    """
    if v is None:
        return v

    normalized = v.strip().upper()
    if not _CREDENTIAL_RE.match(normalized):
        raise ValueError(
            "Formato inválido de registro profissional. "
            "Use só o número (ex.: 123456) ou com sufixo (ex.: 12345-G/SP)"
        )
    return normalized
