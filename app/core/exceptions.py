"""
Exceções de domínio (as regras de negócio).
Elas não sabem nada de HTTP: os services levantam a exceção e quem traduz pro
status code certo é o main.py. Assim a regra de negócio fica separada do HTTP.
"""


class ConflictError(Exception):
    """Quando o dado bate com um que já existe (ex.: CPF repetido).

    O main.py transforma isso num HTTP 409.

    `conflict_with` é um dado opcional (dict) sobre o registro que já existe —
    ex.: id, nome e se está ativo. Serve pra UI oferecer reativar em vez de só
    dizer "já existe". Continua sem saber nada de HTTP: é só um dado de domínio.
    """

    def __init__(self, message: str, *, conflict_with: dict | None = None):
        super().__init__(message)
        self.conflict_with = conflict_with


class NotFoundError(Exception):
    """Quando apontamos pra algo que não existe (ex.: client_id de uma anamnese).

    O main.py transforma isso num HTTP 404.
    """
