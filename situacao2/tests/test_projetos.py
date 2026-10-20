"""Regras de negócio dos projetos."""
import pytest

from app.models import Projeto, Tarefa, db
from app.models import servicos
from app.models.erros import ErroNaoEncontrado, ErroValidacao


def test_criar_projeto_com_nome_e_descricao(app):
    projeto = servicos.criar_projeto("TCC", "Trabalho de conclusão de curso")

    assert projeto.id is not None
    assert projeto.nome == "TCC"
    assert projeto.descricao == "Trabalho de conclusão de curso"
    assert db.session.get(Projeto, projeto.id) is not None


def test_criar_projeto_sem_descricao(app):
    projeto = servicos.criar_projeto("Mudança", "")

    assert projeto.descricao is None


def test_criar_projeto_remove_espacos_das_pontas(app):
    projeto = servicos.criar_projeto("   TCC   ")

    assert projeto.nome == "TCC"


@pytest.mark.parametrize("nome", ["", "   ", None])
def test_nao_permite_projeto_sem_nome(app, nome):
    with pytest.raises(ErroValidacao) as erro:
        servicos.criar_projeto(nome)

    assert erro.value.mensagem == "Informe o nome do projeto."
    assert Projeto.query.count() == 0


def test_nao_permite_nome_de_projeto_muito_longo(app):
    with pytest.raises(ErroValidacao):
        servicos.criar_projeto("x" * 101)


def test_nao_permite_descricao_muito_longa(app):
    with pytest.raises(ErroValidacao):
        servicos.criar_projeto("TCC", "x" * 501)


def test_nao_permite_dois_projetos_com_o_mesmo_nome(app):
    servicos.criar_projeto("TCC")

    with pytest.raises(ErroValidacao) as erro:
        servicos.criar_projeto("tcc")

    assert erro.value.mensagem == "Já existe um projeto com esse nome."
    assert Projeto.query.count() == 1


def test_listar_projetos_em_ordem_alfabetica(app):
    servicos.criar_projeto("Viagem")
    servicos.criar_projeto("Casa")

    nomes = [p.nome for p in servicos.listar_projetos()]

    assert nomes == ["Casa", "Viagem"]


def test_editar_projeto(app):
    projeto = servicos.criar_projeto("TCC")

    servicos.editar_projeto(projeto.id, "TCC 2026", "Nova descrição")

    atualizado = servicos.obter_projeto(projeto.id)
    assert atualizado.nome == "TCC 2026"
    assert atualizado.descricao == "Nova descrição"


def test_editar_projeto_mantendo_o_mesmo_nome(app):
    projeto = servicos.criar_projeto("TCC")

    servicos.editar_projeto(projeto.id, "TCC", "Só mudei a descrição")

    assert servicos.obter_projeto(projeto.id).descricao == "Só mudei a descrição"


def test_editar_projeto_com_nome_de_outro_projeto(app):
    servicos.criar_projeto("Casa")
    projeto = servicos.criar_projeto("TCC")

    with pytest.raises(ErroValidacao):
        servicos.editar_projeto(projeto.id, "Casa", None)


def test_obter_projeto_inexistente(app):
    with pytest.raises(ErroNaoEncontrado) as erro:
        servicos.obter_projeto(999)

    assert erro.value.mensagem == "Projeto não encontrado."


def test_excluir_projeto_exclui_tambem_as_suas_tarefas(app):
    projeto = servicos.criar_projeto("TCC")
    servicos.criar_tarefa(projeto.id, "Escrever introdução")
    servicos.criar_tarefa(projeto.id, "Revisar texto")
    outro = servicos.criar_projeto("Casa")
    servicos.criar_tarefa(outro.id, "Pintar parede")

    servicos.excluir_projeto(projeto.id)

    assert db.session.get(Projeto, projeto.id) is None
    assert Tarefa.query.filter_by(projeto_id=projeto.id).count() == 0
    # As tarefas de outros projetos continuam lá.
    assert Tarefa.query.filter_by(projeto_id=outro.id).count() == 1


def test_excluir_projeto_inexistente(app):
    with pytest.raises(ErroNaoEncontrado):
        servicos.excluir_projeto(999)


class TestProgresso:
    def test_projeto_sem_tarefas_tem_progresso_zero(self, app):
        projeto = servicos.criar_projeto("TCC")

        assert projeto.progresso == 0

    def test_progresso_e_concluidas_sobre_o_total(self, app):
        projeto = servicos.criar_projeto("TCC")
        t1 = servicos.criar_tarefa(projeto.id, "Tarefa 1")
        servicos.criar_tarefa(projeto.id, "Tarefa 2")
        servicos.criar_tarefa(projeto.id, "Tarefa 3")
        t4 = servicos.criar_tarefa(projeto.id, "Tarefa 4")

        servicos.concluir_tarefa(t1.id)
        servicos.concluir_tarefa(t4.id)

        assert projeto.total_tarefas == 4
        assert projeto.tarefas_concluidas == 2
        assert projeto.progresso == 50

    def test_progresso_e_arredondado_para_inteiro(self, app):
        projeto = servicos.criar_projeto("TCC")
        t1 = servicos.criar_tarefa(projeto.id, "Tarefa 1")
        servicos.criar_tarefa(projeto.id, "Tarefa 2")
        servicos.criar_tarefa(projeto.id, "Tarefa 3")

        servicos.concluir_tarefa(t1.id)

        assert projeto.progresso == 33

    def test_todas_concluidas_e_cem_por_cento(self, app):
        projeto = servicos.criar_projeto("TCC")
        tarefa = servicos.criar_tarefa(projeto.id, "Única tarefa")

        servicos.concluir_tarefa(tarefa.id)

        assert projeto.progresso == 100

    def test_progresso_volta_ao_reabrir_tarefa(self, app):
        projeto = servicos.criar_projeto("TCC")
        tarefa = servicos.criar_tarefa(projeto.id, "Única tarefa")
        servicos.concluir_tarefa(tarefa.id)

        servicos.reabrir_tarefa(tarefa.id)

        assert projeto.progresso == 0
