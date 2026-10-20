"""Testes das rotas (controllers): respostas, redirecionamentos e mensagens ao usuário."""
from datetime import date, timedelta

from app.models import Projeto, Tarefa
from app.models import servicos


def mensagens(client):
    """Mensagens (flash) guardadas na sessão para a próxima página."""
    with client.session_transaction() as sessao:
        return [texto for _categoria, texto in sessao.get("_flashes", [])]


def test_pagina_inicial_redireciona_para_projetos(client):
    resposta = client.get("/")

    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/projetos")


def test_lista_de_projetos_abre(client, app):
    servicos.criar_projeto("TCC")

    resposta = client.get("/projetos")

    assert resposta.status_code == 200
    assert "TCC" in resposta.get_data(as_text=True)


def test_cadastrar_projeto_pelo_formulario(client, app):
    resposta = client.post("/projetos", data={"nome": "TCC", "descricao": ""})

    assert resposta.status_code == 302
    assert Projeto.query.count() == 1
    assert "Projeto criado com sucesso." in mensagens(client)


def test_cadastrar_projeto_sem_nome_mostra_erro_e_mantem_o_formulario(client, app):
    resposta = client.post("/projetos", data={"nome": "", "descricao": "Algo"})

    assert resposta.status_code == 400
    html = resposta.get_data(as_text=True)
    assert "Informe o nome do projeto." in html
    assert "Algo" in html  # o que o usuário digitou não se perde
    assert Projeto.query.count() == 0


def test_editar_projeto_pelo_formulario(client, app):
    projeto = servicos.criar_projeto("TCC")

    resposta = client.post(f"/projetos/{projeto.id}/editar", data={"nome": "TCC 2026", "descricao": ""})

    assert resposta.status_code == 302
    assert servicos.obter_projeto(projeto.id).nome == "TCC 2026"
    assert "Projeto atualizado com sucesso." in mensagens(client)


def test_excluir_projeto_pelo_formulario(client, app):
    projeto = servicos.criar_projeto("TCC")
    servicos.criar_tarefa(projeto.id, "Tarefa")

    resposta = client.post(f"/projetos/{projeto.id}/excluir")

    assert resposta.status_code == 302
    assert Projeto.query.count() == 0
    assert Tarefa.query.count() == 0
    assert "Projeto e suas tarefas foram excluídos." in mensagens(client)


def test_pagina_do_projeto_mostra_tarefas_e_progresso(client, app):
    projeto = servicos.criar_projeto("TCC")
    feita = servicos.criar_tarefa(projeto.id, "Tarefa feita")
    servicos.criar_tarefa(projeto.id, "Tarefa pendente")
    servicos.concluir_tarefa(feita.id)

    html = client.get(f"/projetos/{projeto.id}").get_data(as_text=True)

    assert "Tarefa feita" in html
    assert "Tarefa pendente" in html
    assert "50%" in html


def test_filtro_de_atrasadas_na_pagina_do_projeto(client, app):
    projeto = servicos.criar_projeto("TCC")
    servicos.criar_tarefa(projeto.id, "Tarefa atrasada", date.today() - timedelta(days=2))
    servicos.criar_tarefa(projeto.id, "Tarefa no prazo", date.today() + timedelta(days=2))

    html = client.get(f"/projetos/{projeto.id}?filtro=atrasadas").get_data(as_text=True)

    assert "Tarefa atrasada" in html
    assert "Tarefa no prazo" not in html


def test_pagina_de_atrasadas_de_todos_os_projetos(client, app):
    projeto = servicos.criar_projeto("TCC")
    servicos.criar_tarefa(projeto.id, "Tarefa atrasada", date.today() - timedelta(days=2))

    resposta = client.get("/tarefas/atrasadas")

    assert resposta.status_code == 200
    assert "Tarefa atrasada" in resposta.get_data(as_text=True)


def test_cadastrar_tarefa_pelo_formulario(client, app):
    projeto = servicos.criar_projeto("TCC")

    resposta = client.post(f"/projetos/{projeto.id}/tarefas", data={"titulo": "Nova", "prazo": "2026-11-01"})

    assert resposta.status_code == 302
    assert Tarefa.query.count() == 1
    assert "Tarefa criada com sucesso." in mensagens(client)


def test_cadastrar_tarefa_sem_titulo_mostra_erro(client, app):
    projeto = servicos.criar_projeto("TCC")

    resposta = client.post(f"/projetos/{projeto.id}/tarefas", data={"titulo": "", "prazo": ""})

    assert resposta.status_code == 400
    assert "Informe o título da tarefa." in resposta.get_data(as_text=True)
    assert Tarefa.query.count() == 0


def test_alternar_tarefa_pelo_formulario(client, app):
    projeto = servicos.criar_projeto("TCC")
    tarefa = servicos.criar_tarefa(projeto.id, "Tarefa")

    resposta = client.post(f"/tarefas/{tarefa.id}/alternar")

    assert resposta.status_code == 302
    assert servicos.obter_tarefa(tarefa.id).concluida
    assert "Tarefa marcada como concluída." in mensagens(client)


def test_alternar_tarefa_via_javascript_responde_json(client, app):
    projeto = servicos.criar_projeto("TCC")
    tarefa = servicos.criar_tarefa(projeto.id, "Tarefa")

    resposta = client.post(f"/tarefas/{tarefa.id}/alternar", headers={"Accept": "application/json"})

    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert dados["status"] == "concluida"
    assert dados["progresso"] == 100
    assert dados["mensagem"] == "Tarefa marcada como concluída."


def test_editar_tarefa_pelo_formulario(client, app):
    projeto = servicos.criar_projeto("TCC")
    tarefa = servicos.criar_tarefa(projeto.id, "Tarefa")

    resposta = client.post(f"/tarefas/{tarefa.id}/editar", data={"titulo": "Tarefa editada", "prazo": ""})

    assert resposta.status_code == 302
    assert servicos.obter_tarefa(tarefa.id).titulo == "Tarefa editada"
    assert "Tarefa atualizada com sucesso." in mensagens(client)


def test_excluir_tarefa_pelo_formulario(client, app):
    projeto = servicos.criar_projeto("TCC")
    tarefa = servicos.criar_tarefa(projeto.id, "Tarefa")

    resposta = client.post(f"/tarefas/{tarefa.id}/excluir")

    assert resposta.status_code == 302
    assert Tarefa.query.count() == 0
    assert "Tarefa excluída." in mensagens(client)


def test_projeto_inexistente_mostra_mensagem_amigavel(client, app):
    resposta = client.get("/projetos/999")

    assert resposta.status_code == 404
    html = resposta.get_data(as_text=True)
    assert "Projeto não encontrado." in html
    assert "Traceback" not in html


def test_pagina_inexistente_mostra_mensagem_amigavel(client, app):
    resposta = client.get("/nao-existe")

    assert resposta.status_code == 404
    assert "Página não encontrada." in resposta.get_data(as_text=True)


def test_erro_inesperado_no_banco_nao_mostra_erro_tecnico(client, app, monkeypatch):
    from sqlalchemy.exc import OperationalError

    def banco_fora_do_ar(*args, **kwargs):
        raise OperationalError("SELECT ...", {}, Exception("database is locked"))

    monkeypatch.setattr(servicos, "listar_projetos", banco_fora_do_ar)

    resposta = client.get("/projetos")

    assert resposta.status_code == 500
    html = resposta.get_data(as_text=True)
    assert "database is locked" not in html
    assert "Algo deu errado" in html
