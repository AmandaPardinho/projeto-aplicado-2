"""
Entrypoint da aplicação FastAPI.
Cria a instância do app, configura middlewares e registra os routers.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import instructor as instructor_router
from app.api import client as client_router
from app.api import plan as plan_router
from app.api import anamnesis as anamnesis_router
from app.core.exceptions import ConflictError, NotFoundError


app = FastAPI(
    title="Studio Pilates API",
    description="API de automatização de atendimento de Studio de Pilates",
    version="0.1.0",
)


# CORS — permite que o frontend (rodando em outra porta) chame a API.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler global: ValueError (regra de negócio violada) → HTTP 400.
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Converte ValueError lançado nos services em HTTP 400 com mensagem amigável."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

# Exception handler global: ConflictError (recurso duplicado) → HTTP 409.
@app.exception_handler(ConflictError)
async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
    """Converte ConflictError lançado nos services em HTTP 409 Conflict.

    Se a exceção trouxer `conflict_with` (dados do registro existente), inclui
    no corpo — é o que permite o front oferecer reativar em vez de só barrar.
    """
    content = {"detail": str(exc)}
    if getattr(exc, "conflict_with", None):
        content["conflict_with"] = exc.conflict_with
    return JSONResponse(status_code=409, content=content)

# Exception handler global: NotFoundError (recurso referenciado não existe) → HTTP 404.
@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """Converte NotFoundError lançado nos services em HTTP 404 Not Found."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )

# Registra os routers (por entidade)
app.include_router(client_router.router)
app.include_router(instructor_router.router)
app.include_router(plan_router.router)
app.include_router(anamnesis_router.router)

@app.get("/", tags=["Health"])
def root():
    """Health check — retorna 200 se a API está no ar."""
    return {"status": "ok", "service": "studio-pilates-api"}
