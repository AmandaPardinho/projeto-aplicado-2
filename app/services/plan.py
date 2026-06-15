"""
Service do Plan.
É aqui que ficam as regras de negócio do plano: o service chama o repository,
trata os casos especiais e devolve os dados prontos pro router.
"""

from typing import Optional
from uuid import UUID

from app.schemas.plan import Plan, PlanCreate, PlanUpdate
from app.repositories import plan as repo


def create(data: PlanCreate) -> Plan:
    """Cria um plano novo."""
    return repo.create(data)


def get_all() -> list[Plan]:
    """Lista todos os planos."""
    return repo.get_all()


def get_by_id(plan_id: UUID) -> Optional[Plan]:
    """Busca um plano pelo ID. Devolve None se não achar."""
    return repo.get_by_id(plan_id)


def update(plan_id: UUID, data: PlanUpdate) -> Optional[Plan]:
    """Atualiza um plano que já existe."""
    # exclude_none=True manda pro banco só o que veio preenchido, então dá pra
    # mudar um campo só sem zerar o resto. mode="json" deixa os tipos (Decimal,
    # UUID, datetime) no formato que o Supabase aceita.
    update_data = data.model_dump(mode="json", exclude_none=True)

    # Corpo vazio é erro de quem chamou, não nosso. Esse ValueError vira um
    # HTTP 400 lá no main.py (tem um handler que cuida disso).
    if not update_data:
        raise ValueError("Nenhum campo para atualizar")

    # Se o PUT mandar is_active=true, aproveito pra "ressuscitar" o registro
    # limpando o deleted_at. É o contrário do que o DELETE faz (soft-delete).
    if update_data.get("is_active") is True:
        update_data["deleted_at"] = None

    return repo.update(plan_id, update_data)


def delete(plan_id: UUID) -> bool:
    """Remove o plano (soft-delete). True se removeu, False se o ID não existia."""
    return repo.delete(plan_id)
