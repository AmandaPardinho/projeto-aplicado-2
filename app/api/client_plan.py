"""
Router (controller) da Matrícula (client_plan).
Define os endpoints HTTP da entidade.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.schemas.client_plan import (
    ClientPlan,
    ClientPlanCreate,
    ClientPlanRead,
    ClientPlanUpdate,
)
from app.services import client_plan as service

router = APIRouter(prefix="/client_plans", tags=["Client Plans"])


@router.post(
    "",
    response_model=ClientPlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova matrícula",
)
def create_client_plan(payload: ClientPlanCreate) -> ClientPlan:
    """Matricula uma aluna num plano (a matrícula vale 1 ano)."""
    return service.create(payload)


@router.get(
    "",
    response_model=list[ClientPlanRead],
    summary="Lista todas as matrículas",
)
def list_client_plans() -> list[ClientPlan]:
    """Retorna todas as matrículas cadastradas."""
    return service.get_all()


@router.get(
    "/{client_plan_id}",
    response_model=ClientPlanRead,
    summary="Busca uma matrícula pelo ID",
)
def get_client_plan(client_plan_id: UUID) -> ClientPlan:
    """Retorna a matrícula com o ID informado, ou 404 se não existir."""
    client_plan = service.get_by_id(client_plan_id)
    if client_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Matrícula {client_plan_id} não encontrada",
        )
    return client_plan


@router.put(
    "/{client_plan_id}",
    response_model=ClientPlanRead,
    summary="Atualiza uma matrícula",
)
def update_client_plan(client_plan_id: UUID, payload: ClientPlanUpdate) -> ClientPlan:
    """Atualiza campos da matrícula pelo ID."""
    client_plan = service.update(client_plan_id, payload)
    if client_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Matrícula {client_plan_id} não encontrada",
        )
    return client_plan


@router.delete(
    "/{client_plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove uma matrícula",
)
def delete_client_plan(client_plan_id: UUID) -> None:
    """Remove a matrícula pelo ID (soft-delete)."""
    deleted = service.delete(client_plan_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Matrícula {client_plan_id} não encontrada",
        )
