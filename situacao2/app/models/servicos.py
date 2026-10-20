"""Regras de negócio do sistema.

Os controllers chamam só estas funções; aqui ficam as validações, o acesso ao banco
e o tratamento de erros de banco (rollback).
"""
from contextlib import contextmanager
from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.banco import db
from app.models.erros import ErroNaoEncontrado, ErroValidacao
from app.models.projeto import Projeto
from app.models.tarefa import PENDENTE, Tarefa

MSG_NOME_VAZIO = "Informe o nome do projeto."
MSG_NOME_LONGO = f"O nome do projeto pode ter no máximo {Projeto.NOME_MAX} caracteres."
MSG_NOME_REPETIDO = "Já existe um projeto com esse nome."
MSG_DESCRICAO_LONGA = f"A descrição pode ter no máximo {Projeto.DESCRICAO_MAX} caracteres."
MSG_TITULO_VAZIO = "Informe o título da tarefa."
MSG_TITULO_LONGO = f"O título da tarefa pode ter no máximo {Tarefa.TITULO_MAX} caracteres."
MSG_PRAZO_INVALIDO = "Informe um prazo válido (dia/mês/ano)."


@contextmanager
def _transacao():
    """Grava as alterações; se o banco falhar, desfaz tudo e repassa o erro."""
    try:
        yield
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise


# ---------- validações ----------

def _texto_limpo(valor):
    return (valor or "").strip()


def _validar_nome(nome, ignorar_id=None):
    nome = _texto_limpo(nome)
    if not nome:
        raise ErroValidacao(MSG_NOME_VAZIO)
    if len(nome) > Projeto.NOME_MAX:
        raise ErroValidacao(MSG_NOME_LONGO)
    consulta = Projeto.query.filter(func.lower(Projeto.nome) == nome.lower())
    if ignorar_id is not None:
        consulta = consulta.filter(Projeto.id != ignorar_id)
    if consulta.first() is not None:
        raise ErroValidacao(MSG_NOME_REPETIDO)
    return nome


def _validar_descricao(descricao):
    descricao = _texto_limpo(descricao)
    if len(descricao) > Projeto.DESCRICAO_MAX:
        raise ErroValidacao(MSG_DESCRICAO_LONGA)
    return descricao or None


def _validar_titulo(titulo):
    titulo = _texto_limpo(titulo)
    if not titulo:
        raise ErroValidacao(MSG_TITULO_VAZIO)
    if len(titulo) > Tarefa.TITULO_MAX:
        raise ErroValidacao(MSG_TITULO_LONGO)
    return titulo


def _converter_prazo(prazo):
    """Aceita date, texto AAAA-MM-DD (campo date do HTML) ou DD/MM/AAAA. Vazio = sem prazo."""
    if prazo is None or isinstance(prazo, date):
        return prazo
    texto = prazo.strip()
    if not texto:
        return None
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    raise ErroValidacao(MSG_PRAZO_INVALIDO)


def _salvar_projeto(projeto):
    try:
        with _transacao():
            db.session.add(projeto)
    except IntegrityError:
        # Outro cadastro com o mesmo nome entrou ao mesmo tempo.
        raise ErroValidacao(MSG_NOME_REPETIDO)
    return projeto


# ---------- projetos ----------

def listar_projetos():
    return Projeto.query.order_by(func.lower(Projeto.nome)).all()


def obter_projeto(projeto_id):
    projeto = db.session.get(Projeto, projeto_id)
    if projeto is None:
        raise ErroNaoEncontrado("Projeto não encontrado.")
    return projeto


def criar_projeto(nome, descricao=None):
    projeto = Projeto(nome=_validar_nome(nome), descricao=_validar_descricao(descricao))
    return _salvar_projeto(projeto)


def editar_projeto(projeto_id, nome, descricao):
    projeto = obter_projeto(projeto_id)
    novo_nome = _validar_nome(nome, ignorar_id=projeto.id)
    nova_descricao = _validar_descricao(descricao)
    projeto.nome = novo_nome
    projeto.descricao = nova_descricao
    return _salvar_projeto(projeto)


def excluir_projeto(projeto_id):
    projeto = obter_projeto(projeto_id)
    with _transacao():
        db.session.delete(projeto)


# ---------- tarefas ----------

def _ordem_das_tarefas():
    """Pendentes antes das concluídas; depois pelo prazo mais próximo; sem prazo por último."""
    return (
        (Tarefa.status != PENDENTE),
        Tarefa.prazo.is_(None),
        Tarefa.prazo,
        Tarefa.id,
    )


def _filtro_atrasadas(hoje):
    return (Tarefa.status == PENDENTE, Tarefa.prazo.isnot(None), Tarefa.prazo < hoje)


def listar_tarefas(projeto_id, apenas_atrasadas=False, hoje=None):
    obter_projeto(projeto_id)
    consulta = Tarefa.query.filter(Tarefa.projeto_id == projeto_id)
    if apenas_atrasadas:
        consulta = consulta.filter(*_filtro_atrasadas(hoje or date.today()))
    return consulta.order_by(*_ordem_das_tarefas()).all()


def listar_tarefas_atrasadas(hoje=None, projeto_id=None):
    consulta = Tarefa.query.filter(*_filtro_atrasadas(hoje or date.today()))
    if projeto_id is not None:
        consulta = consulta.filter(Tarefa.projeto_id == projeto_id)
    return consulta.order_by(Tarefa.prazo, Tarefa.id).all()


def obter_tarefa(tarefa_id):
    tarefa = db.session.get(Tarefa, tarefa_id)
    if tarefa is None:
        raise ErroNaoEncontrado("Tarefa não encontrada.")
    return tarefa


def criar_tarefa(projeto_id, titulo, prazo=None):
    projeto = obter_projeto(projeto_id)
    tarefa = Tarefa(projeto=projeto, titulo=_validar_titulo(titulo), prazo=_converter_prazo(prazo))
    with _transacao():
        db.session.add(tarefa)
    return tarefa


def editar_tarefa(tarefa_id, titulo, prazo):
    tarefa = obter_tarefa(tarefa_id)
    novo_titulo = _validar_titulo(titulo)
    novo_prazo = _converter_prazo(prazo)
    with _transacao():
        tarefa.titulo = novo_titulo
        tarefa.prazo = novo_prazo
    return tarefa


def excluir_tarefa(tarefa_id):
    tarefa = obter_tarefa(tarefa_id)
    with _transacao():
        db.session.delete(tarefa)


def concluir_tarefa(tarefa_id):
    tarefa = obter_tarefa(tarefa_id)
    with _transacao():
        tarefa.concluir()
    return tarefa


def reabrir_tarefa(tarefa_id):
    tarefa = obter_tarefa(tarefa_id)
    with _transacao():
        tarefa.reabrir()
    return tarefa


def alternar_tarefa(tarefa_id):
    tarefa = obter_tarefa(tarefa_id)
    with _transacao():
        if tarefa.concluida:
            tarefa.reabrir()
        else:
            tarefa.concluir()
    return tarefa
