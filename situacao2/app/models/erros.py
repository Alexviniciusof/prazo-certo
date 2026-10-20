"""Erros de regra de negócio. A mensagem de cada um pode ser mostrada ao usuário."""


class ErroNegocio(Exception):
    def __init__(self, mensagem):
        super().__init__(mensagem)
        self.mensagem = mensagem


class ErroValidacao(ErroNegocio):
    """Dado informado pelo usuário é inválido (campo vazio, muito longo, repetido...)."""


class ErroNaoEncontrado(ErroNegocio):
    """Projeto ou tarefa não existe."""
