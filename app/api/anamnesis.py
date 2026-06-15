"""
Router (controller) da Anamnesis.
Define os endpoints HTTP da entidade.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.schemas.anamnesis import Anamnesis, AnamnesisCreate, AnamnesisRead, AnamnesisUpdate
from app.services import anamnesis as service

router = APIRouter(prefix="/anamneses", tags=["Anamneses"])

@router.post(
    "",
    response_model=AnamnesisRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova anamnese",
)
def create_anamnesis(payload: AnamnesisCreate) -> Anamnesis:
    """Cria uma nova anamnese para um cliente."""
    return service.create(payload)

@router.get(
    "",
    response_model=list[AnamnesisRead],
    summary="Lista todas as anamneses",
)
def list_anamneses() -> list[Anamnesis]:
    """Retorna todas as anamneses cadastradas."""
    return service.get_all()


@router.get(
    "/{anamnesis_id}",
    response_model=AnamnesisRead,
    summary="Busca uma anamnese pelo ID",
)
def get_anamnesis(anamnesis_id: UUID) -> Anamnesis:
    """Retorna a anamnese com o ID informado, ou 404 se não existir."""
    anamnesis = service.get_by_id(anamnesis_id)
    if anamnesis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anamnese {anamnesis_id} não encontrada",
        )
    return anamnesis

@router.put(
    "/{anamnesis_id}",
    response_model=AnamnesisRead,
    summary="Atualiza uma anamnese",
)
def update_anamnesis(anamnesis_id: UUID, payload: AnamnesisUpdate) -> Anamnesis:
    """Atualiza campos da anamnese pelo ID."""
    anamnesis = service.update(anamnesis_id, payload)
    if anamnesis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anamnese {anamnesis_id} não encontrada",
        )
    return anamnesis


@router.delete(
    "/{anamnesis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove uma anamnese",
)
def delete_anamnesis(anamnesis_id: UUID) -> None:
    """Remove a anamnese pelo ID."""
    deleted = service.delete(anamnesis_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anamnese {anamnesis_id} não encontrada",
        )
