"""
Router (controller) do Instructor.
Define os endpoints HTTP da entidade.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.schemas.instructor import Instructor, InstructorCreate, InstructorRead, InstructorUpdate
from app.services import instructor as service

router = APIRouter(prefix="/instructors", tags=["Instructors"])

@router.post(
    "",
    response_model=InstructorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo instrutor",
)
def create_instructor(payload: InstructorCreate) -> Instructor:
    """Cria um novo instrutor no sistema."""
    return service.create(payload)


@router.get(
    "",
    response_model=list[InstructorRead],
    summary="Lista todos os instrutores",
)
def list_instructors() -> list[Instructor]:
    """Retorna todos os instrutores cadastrados."""
    return service.get_all()


@router.get(
    "/{instructor_id}",
    response_model=InstructorRead,
    summary="Busca um instrutor pelo ID",
)
def get_instructor(instructor_id: UUID) -> Instructor:
    """Retorna o instrutor com o ID informado, ou 404 se não existir."""
    instructor = service.get_by_id(instructor_id)
    if instructor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrutor {instructor_id} não encontrado",
        )
    return instructor


@router.put(
    "/{instructor_id}",
    response_model=InstructorRead,
    summary="Atualiza um instrutor",
)
def update_instructor(instructor_id: UUID, payload: InstructorUpdate) -> Instructor:
    """Atualiza campos do instrutor pelo ID."""
    instructor = service.update(instructor_id, payload)
    if instructor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrutor {instructor_id} não encontrado",
        )
    return instructor


@router.delete(
    "/{instructor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um instrutor",
)
def delete_instructor(instructor_id: UUID) -> None:
    """Remove o instrutor pelo ID."""
    deleted = service.delete(instructor_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrutor {instructor_id} não encontrado",
        )
