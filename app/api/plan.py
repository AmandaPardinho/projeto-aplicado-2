"""
Router (controller) do Plan.
Define os endpoints HTTP da entidade.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.schemas.plan import Plan, PlanCreate, PlanRead, PlanUpdate
from app.services import plan as service

router = APIRouter(prefix="/plans", tags=["Plans"])

@router.post(
    "",
    response_model=PlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo plano",
)
def create_plan(payload: PlanCreate) -> Plan:
    """Cria um novo plano no sistema."""
    return service.create(payload)

@router.get(
    "",
    response_model=list[PlanRead],
    summary="Lista todos os planos",
)
def list_plans() -> list[Plan]:
    """Retorna todos os planos cadastrados."""
    return service.get_all()


@router.get(
    "/{plan_id}",
    response_model=PlanRead,
    summary="Busca um plano pelo ID",
)
def get_plan(plan_id: UUID) -> Plan:
    """Retorna o plano com o ID informado, ou 404 se não existir."""
    plan = service.get_by_id(plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plano {plan_id} não encontrado",
        )
    return plan

@router.put(
    "/{plan_id}",
    response_model=PlanRead,
    summary="Atualiza um plano",
)
def update_plan(plan_id: UUID, payload: PlanUpdate) -> Plan:
    """Atualiza campos do plano pelo ID."""
    plan = service.update(plan_id, payload)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plano {plan_id} não encontrado",
        )
    return plan


@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um plano",
)
def delete_plan(plan_id: UUID) -> None:
    """Remove o plano pelo ID."""
    deleted = service.delete(plan_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plano {plan_id} não encontrado",
        )
