"""Regras de negócio das tarefas."""
from datetime import date, timedelta

import pytest

from app.models import Tarefa
from app.models import servicos
from app.models.erros import ErroNaoEncontrado, ErroValidacao


@pytest.fixture
def projeto(app):
    return servicos.criar_projeto("TCC")


def test_criar_tarefa_em_um_projeto(projeto):
    tarefa = servicos.criar_tarefa(projeto.id, "Escrever introdução", date(2026, 11, 1))

    assert tarefa.id is not None
    assert tarefa.titulo == "Escrever introdução"
    assert tarefa.prazo == date(2026, 11, 1)
    assert tarefa.status == "pendente"
    assert tarefa.concluida_em is None
    assert tarefa.projeto_id == projeto.id
    assert tarefa in projeto.tarefas


def test_criar_tarefa_sem_prazo(projeto):
    tarefa = servicos.criar_tarefa(projeto.id, "Escrever introdução")

    assert tarefa.prazo is None


def test_criar_tarefa_com_prazo_em_texto(projeto):
    """O formulário HTML envia o prazo como texto AAAA-MM-DD."""
    tarefa = servicos.criar_tarefa(projeto.id, "Escrever introdução", "2026-11-01")

    assert tarefa.prazo == date(2026, 11, 1)


def test_prazo_em_texto_vazio_vira_sem_prazo(projeto):
    tarefa = servicos.criar_tarefa(projeto.id, "Escrever introdução", "")

    assert tarefa.prazo is None


@pytest.mark.parametrize("titulo", ["", "   ", None])
def test_nao_permite_tarefa_sem_titulo(projeto, titulo):
    with pytest.raises(ErroValidacao) as erro:
        servicos.criar_tarefa(projeto.id, titulo)

    assert erro.value.mensagem == "Informe o título da tarefa."
    assert Tarefa.query.count() == 0


def test_nao_permite_titulo_muito_longo(projeto):
    with pytest.raises(ErroValidacao):
        servicos.criar_tarefa(projeto.id, "x" * 151)


def test_nao_permite_prazo_invalido(projeto):
    with pytest.raises(ErroValidacao) as erro:
        servicos.criar_tarefa(projeto.id, "Escrever introdução", "31/02/2026")

    assert erro.value.mensagem == "Informe um prazo válido (dia/mês/ano)."


def test_nao_permite_tarefa_em_projeto_inexistente(app):
    with pytest.raises(ErroNaoEncontrado):
        servicos.criar_tarefa(999, "Tarefa perdida")


def test_listar_tarefas_do_projeto(projeto):
    servicos.criar_tarefa(projeto.id, "Tarefa A")
    servicos.criar_tarefa(projeto.id, "Tarefa B")
    outro = servicos.criar_projeto("Casa")
    servicos.criar_tarefa(outro.id, "Tarefa de outro projeto")

    titulos = {t.titulo for t in servicos.listar_tarefas(projeto.id)}

    assert titulos == {"Tarefa A", "Tarefa B"}


def test_listar_tarefas_pendentes_primeiro_e_por_prazo(projeto):
    sem_prazo = servicos.criar_tarefa(projeto.id, "Sem prazo")
    depois = servicos.criar_tarefa(projeto.id, "Depois", date(2026, 12, 1))
    antes = servicos.criar_tarefa(projeto.id, "Antes", date(2026, 11, 1))
    feita = servicos.criar_tarefa(projeto.id, "Feita", date(2026, 10, 1))
    servicos.concluir_tarefa(feita.id)

    ordem = [t.id for t in servicos.listar_tarefas(projeto.id)]

    assert ordem == [antes.id, depois.id, sem_prazo.id, feita.id]


def test_editar_tarefa(projeto):
    tarefa = servicos.criar_tarefa(projeto.id, "Escrever intro")

    servicos.editar_tarefa(tarefa.id, "Escrever introdução", "2026-11-05")

    atualizada = servicos.obter_tarefa(tarefa.id)
    assert atualizada.titulo == "Escrever introdução"
    assert atualizada.prazo == date(2026, 11, 5)


def test_editar_tarefa_sem_titulo(projeto):
    tarefa = servicos.criar_tarefa(projeto.id, "Escrever intro")

    with pytest.raises(ErroValidacao):
        servicos.editar_tarefa(tarefa.id, "  ", None)

    assert servicos.obter_tarefa(tarefa.id).titulo == "Escrever intro"


def test_excluir_tarefa(projeto):
    tarefa = servicos.criar_tarefa(projeto.id, "Escrever introdução")

    servicos.excluir_tarefa(tarefa.id)

    assert Tarefa.query.count() == 0


def test_obter_tarefa_inexistente(app):
    with pytest.raises(ErroNaoEncontrado) as erro:
        servicos.obter_tarefa(999)

    assert erro.value.mensagem == "Tarefa não encontrada."


class TestConcluir:
    def test_marcar_tarefa_como_concluida(self, projeto):
        tarefa = servicos.criar_tarefa(projeto.id, "Escrever introdução")

        servicos.concluir_tarefa(tarefa.id)

        atualizada = servicos.obter_tarefa(tarefa.id)
        assert atualizada.status == "concluida"
        assert atualizada.concluida
        assert atualizada.concluida_em is not None

    def test_desmarcar_tarefa_concluida(self, projeto):
        tarefa = servicos.criar_tarefa(projeto.id, "Escrever introdução")
        servicos.concluir_tarefa(tarefa.id)

        servicos.reabrir_tarefa(tarefa.id)

        atualizada = servicos.obter_tarefa(tarefa.id)
        assert atualizada.status == "pendente"
        assert not atualizada.concluida
        assert atualizada.concluida_em is None

    def test_alternar_status(self, projeto):
        tarefa = servicos.criar_tarefa(projeto.id, "Escrever introdução")

        assert servicos.alternar_tarefa(tarefa.id).status == "concluida"
        assert servicos.alternar_tarefa(tarefa.id).status == "pendente"

    def test_concluir_tarefa_inexistente(self, app):
        with pytest.raises(ErroNaoEncontrado):
            servicos.concluir_tarefa(999)


class TestAtrasadas:
    def test_tarefa_pendente_com_prazo_vencido_esta_atrasada(self, projeto, hoje):
        tarefa = servicos.criar_tarefa(projeto.id, "Vencida", hoje - timedelta(days=1))

        assert tarefa.esta_atrasada(hoje)

    def test_prazo_hoje_ainda_nao_esta_atrasada(self, projeto, hoje):
        tarefa = servicos.criar_tarefa(projeto.id, "Vence hoje", hoje)

        assert not tarefa.esta_atrasada(hoje)

    def test_tarefa_sem_prazo_nunca_esta_atrasada(self, projeto, hoje):
        tarefa = servicos.criar_tarefa(projeto.id, "Sem prazo")

        assert not tarefa.esta_atrasada(hoje)

    def test_tarefa_concluida_nao_esta_atrasada(self, projeto, hoje):
        tarefa = servicos.criar_tarefa(projeto.id, "Feita", hoje - timedelta(days=5))
        servicos.concluir_tarefa(tarefa.id)

        assert not tarefa.esta_atrasada(hoje)

    def test_listar_somente_tarefas_atrasadas_do_projeto(self, projeto, hoje):
        atrasada = servicos.criar_tarefa(projeto.id, "Atrasada", hoje - timedelta(days=3))
        servicos.criar_tarefa(projeto.id, "No prazo", hoje + timedelta(days=3))
        servicos.criar_tarefa(projeto.id, "Vence hoje", hoje)
        servicos.criar_tarefa(projeto.id, "Sem prazo")
        feita = servicos.criar_tarefa(projeto.id, "Vencida mas feita", hoje - timedelta(days=3))
        servicos.concluir_tarefa(feita.id)

        resultado = servicos.listar_tarefas(projeto.id, apenas_atrasadas=True, hoje=hoje)

        assert [t.id for t in resultado] == [atrasada.id]

    def test_listar_atrasadas_de_todos_os_projetos(self, projeto, hoje):
        outro = servicos.criar_projeto("Casa")
        a1 = servicos.criar_tarefa(projeto.id, "Atrasada TCC", hoje - timedelta(days=2))
        a2 = servicos.criar_tarefa(outro.id, "Atrasada Casa", hoje - timedelta(days=1))
        servicos.criar_tarefa(outro.id, "No prazo", hoje + timedelta(days=1))

        resultado = servicos.listar_tarefas_atrasadas(hoje=hoje)

        # Da mais atrasada para a menos atrasada.
        assert [t.id for t in resultado] == [a1.id, a2.id]

    def test_contagem_de_atrasadas_no_projeto(self, projeto, hoje):
        servicos.criar_tarefa(projeto.id, "Atrasada 1", hoje - timedelta(days=1))
        servicos.criar_tarefa(projeto.id, "Atrasada 2", hoje - timedelta(days=9))
        servicos.criar_tarefa(projeto.id, "No prazo", hoje + timedelta(days=1))

        assert projeto.total_atrasadas(hoje) == 2
