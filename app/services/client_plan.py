"""
Service da Matrícula (client_plan).
Regras de negócio: valida as FKs, calcula o vencimento e cuida da regra de
"1 plano ativo por aluna".
"""

from datetime import date
from typing import Optional
from uuid import UUID

from app.schemas.client_plan import ClientPlan, ClientPlanCreate, ClientPlanRead, ClientPlanUpdate
from app.repositories import client_plan as repo
from app.repositories import client as client_repo
from app.repositories import plan as plan_repo
from app.repositories import anamnesis as anamnesis_repo
from app.core.exceptions import ConflictError, NotFoundError


def _to_read(plan: ClientPlan, active_client_ids: Optional[set[str]] = None) -> ClientPlanRead:
    """Acrescenta a flag derivada `anamnesis_pending` a uma matrícula.

    - Na listagem, recebo o conjunto de quem TEM anamnese ativa (1 query só).
    - Num registro isolado (create/get/update), consulto a anamnese daquela aluna.
    Pendente = a aluna não tem nenhuma anamnese ativa.
    """
    if active_client_ids is not None:
        pending = str(plan.client_id) not in active_client_ids
    else:
        anamnesis = anamnesis_repo.get_by_client_id(plan.client_id)
        pending = anamnesis is None or not anamnesis.is_active

    return ClientPlanRead(**plan.model_dump(), anamnesis_pending=pending)


def _add_one_year(d: date) -> date:
    """Soma 1 ano à data. Trata o 29/02 (em ano não bissexto vira 28/02)."""
    try:
        return d.replace(year=d.year + 1)
    except ValueError:
        return d.replace(year=d.year + 1, day=28)


def _active_conflict(active: ClientPlan) -> ConflictError:
    """Monta o 409 da regra "1 plano ativo", levando os dados do plano atual.

    É isso que o front lê pra oferecer a TROCA de plano (em vez de só barrar).
    """
    return ConflictError(
        f"O cliente {active.client_id} já possui um plano ativo",
        conflict_with={
            "id": str(active.id),
            "plan_id": str(active.plan_id),
            "end_date": active.end_date.isoformat(),
            "is_active": active.is_active,
        },
    )


def create(data: ClientPlanCreate) -> ClientPlan:
    """Cria uma matrícula nova."""
    # A aluna precisa existir (senão a FK do banco estouraria num 500 feio).
    if client_repo.get_by_id(data.client_id) is None:
        raise NotFoundError(f"Cliente {data.client_id} não encontrado")

    # O plano também precisa existir.
    if plan_repo.get_by_id(data.plan_id) is None:
        raise NotFoundError(f"Plano {data.plan_id} não encontrado")

    # Regra: 1 aluna -> 1 plano ativo. Se já tem um ativo, devolvo 409 com os
    # dados dele — o front usa isso pra oferecer a TROCA (desativa o atual e cria
    # o novo), uma decisão explícita da recepção.
    active = repo.get_active_by_client_id(data.client_id)
    if active is not None:
        raise _active_conflict(active)

    # start_date é opcional (default: hoje). A matrícula vale 1 ano, então o
    # vencimento é derivado — não é a recepção que digita.
    start = data.start_date or date.today()
    payload = {
        "client_id": str(data.client_id),
        "plan_id": str(data.plan_id),
        "start_date": start.isoformat(),
        "end_date": _add_one_year(start).isoformat(),
    }
    if data.renewal_date is not None:
        payload["renewal_date"] = data.renewal_date.isoformat()

    return _to_read(repo.create(payload))


def get_all() -> list[ClientPlanRead]:
    """Lista todas as matrículas (já com a flag de anamnese pendente)."""
    plans = repo.get_all()
    active_client_ids = anamnesis_repo.get_active_client_ids()
    return [_to_read(p, active_client_ids) for p in plans]


def get_by_id(client_plan_id: UUID) -> Optional[ClientPlanRead]:
    """Busca uma matrícula pelo ID. Devolve None se não achar."""
    plan = repo.get_by_id(client_plan_id)
    return _to_read(plan) if plan is not None else None


def update(client_plan_id: UUID, data: ClientPlanUpdate) -> Optional[ClientPlanRead]:
    """Atualiza uma matrícula que já existe."""
    update_data = data.model_dump(mode="json", exclude_none=True)
    if not update_data:
        raise ValueError("Nenhum campo para atualizar")

    # Reativar (is_active=true) limpa o deleted_at — mesma lógica das outras
    # entidades. Mas aqui tem um cuidado a mais: não posso reativar uma matrícula
    # antiga se a aluna já tem OUTRA ativa (violaria a regra de 1 plano ativo).
    # Checo antes pra devolver um 409 limpo em vez do erro cru do índice único.
    if update_data.get("is_active") is True:
        update_data["deleted_at"] = None
        current = repo.get_by_id(client_plan_id)
        if current is not None:
            active = repo.get_active_by_client_id(current.client_id)
            if active is not None and active.id != current.id:
                raise _active_conflict(active)

    updated = repo.update(client_plan_id, update_data)
    return _to_read(updated) if updated is not None else None


def delete(client_plan_id: UUID) -> bool:
    """Remove a matrícula (soft-delete). True se removeu, False se o ID não existia."""
    return repo.delete(client_plan_id)
