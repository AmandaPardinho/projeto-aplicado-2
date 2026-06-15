"""
Exceções de domínio (as regras de negócio).
Elas não sabem nada de HTTP: os services levantam a exceção e quem traduz pro
status code certo é o main.py. Assim a regra de negócio fica separada do HTTP.
"""


class ConflictError(Exception):
    """Quando o dado bate com um que já existe (ex.: CPF repetido).

    O main.py transforma isso num HTTP 409.
    """


class NotFoundError(Exception):
    """Quando apontamos pra algo que não existe (ex.: client_id de uma anamnese).

    O main.py transforma isso num HTTP 404.
    """
