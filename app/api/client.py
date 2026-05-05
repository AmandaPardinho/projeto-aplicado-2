"""
Router (controller) do Cliente.
Define os endpoints HTTP da entidade.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.schemas.client import Client, ClientCreate, ClientRead, ClientUpdate
from app.services import client as service

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post(
    "",
    response_model = ClientRead,
    status_code =  status.HTTP_201_CREATED,
    summary="Cria um novo cliente",
)
def create_client(payload: ClientCreate) -> Client:
    """Cria um novo cliente no sistema."""
    return service.create(payload)

@router.get(
    "",
    response_model=list[ClientRead],
    summary="Lista todos os clientes",
)
def list_clients() -> list[Client]:
    """Retorna todos os clientes cadastrados."""
    return service.get_all()


@router.get(
    "/{client_id}",
    response_model=ClientRead,
    summary="Busca um cliente pelo ID"
)
def get_client(client_id: UUID) -> Client:
    """Retorna o cliente com o ID informado, ou 404 se não existir."""
    client = service.get_by_id(client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {client_id} não encontrado",
        )
    return client

@router.put(
    "/{client_id}",
    response_model=ClientRead,
    summary="Atualiza um cliente",
)
def update_client(client_id: UUID, payload: ClientUpdate) -> Client:
    """Atualiza campos do cliente pelo ID."""
    client = service.update(client_id, payload)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {client_id} não encontrado",
        )
    return client


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um cliente",
)
def delete_client(client_id: UUID) -> None:
    """Remove o cliente pelo ID."""
    deleted = service.delete(client_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {client_id} não encontrado",
        )