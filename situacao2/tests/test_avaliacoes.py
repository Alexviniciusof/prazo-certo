"""Formulário de avaliação usado pelos colegas na Situação 3."""
import io
from datetime import date, timedelta

import pytest

from app.models import Avaliacao, PrintAvaliacao
from app.models import servicos_avaliacao as avaliacoes
from app.models.erros import ErroValidacao

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100
JPG = b"\xff\xd8\xff\xe0" + b"0" * 100
CHAVE = "chave-de-teste-das-avaliacoes"


def dados_validos(**mudancas):
    dados = {
        "nome": "Maria Souza",
        "data_teste": "2026-10-20",
        "dispositivo": "Celular Android / Chrome",
        "funcionou": "Cadastrei projeto e tarefas, marquei como concluída.",
        "nao_funcionou": "",
        "nao_testado": "Não testei excluir projeto.",
        "sugestoes": "Colocar busca de tarefas.",
        "nota": "5",
    }
    dados.update(mudancas)
    return dados


class TestRegras:
    def test_criar_avaliacao_completa(self, app, hoje):
        avaliacao = avaliacoes.criar_avaliacao(dados_validos(), [("tela.png", PNG)], hoje=hoje)

        assert avaliacao.id is not None
        assert avaliacao.nome == "Maria Souza"
        assert avaliacao.data_teste == date(2026, 10, 20)
        assert avaliacao.nota == 5
        assert avaliacao.nao_funcionou is None
        assert len(avaliacao.prints) == 1
        assert avaliacao.prints[0].tipo == "image/png"

    @pytest.mark.parametrize(
        "campo, mensagem",
        [
            ("nome", "Informe o seu nome."),
            ("funcionou", "Conte o que você testou e funcionou."),
            ("data_teste", "Informe a data do teste."),
        ],
    )
    def test_campos_obrigatorios(self, app, hoje, campo, mensagem):
        with pytest.raises(ErroValidacao) as erro:
            avaliacoes.criar_avaliacao(dados_validos(**{campo: "  "}), hoje=hoje)

        assert erro.value.mensagem == mensagem
        assert Avaliacao.query.count() == 0

    def test_data_no_futuro_nao_e_aceita(self, app, hoje):
        amanha = (hoje + timedelta(days=1)).isoformat()

        with pytest.raises(ErroValidacao, match="futuro"):
            avaliacoes.criar_avaliacao(dados_validos(data_teste=amanha), hoje=hoje)

    @pytest.mark.parametrize("nota", ["0", "6", "abc"])
    def test_nota_fora_de_1_a_5(self, app, hoje, nota):
        with pytest.raises(ErroValidacao, match="1 a 5"):
            avaliacoes.criar_avaliacao(dados_validos(nota=nota), hoje=hoje)

    def test_nota_e_opcional(self, app, hoje):
        assert avaliacoes.criar_avaliacao(dados_validos(nota=""), hoje=hoje).nota is None

    def test_arquivo_que_nao_e_imagem_e_recusado(self, app, hoje):
        with pytest.raises(ErroValidacao, match="não é uma imagem"):
            avaliacoes.criar_avaliacao(dados_validos(), [("virus.png", b"MZ\x90\x00 executavel")], hoje=hoje)

        assert PrintAvaliacao.query.count() == 0

    def test_no_maximo_tres_prints(self, app, hoje):
        with pytest.raises(ErroValidacao, match="no máximo 3"):
            avaliacoes.criar_avaliacao(dados_validos(), [("a.png", PNG)] * 4, hoje=hoje)

    def test_print_maior_que_3_mb_e_recusado(self, app, hoje):
        grande = PNG + b"0" * (3 * 1024 * 1024)

        with pytest.raises(ErroValidacao, match="3 MB"):
            avaliacoes.criar_avaliacao(dados_validos(), [("grande.png", grande)], hoje=hoje)

    def test_tipo_vem_do_conteudo_e_nao_do_nome(self, app, hoje):
        avaliacao = avaliacoes.criar_avaliacao(dados_validos(), [("foto.png", JPG)], hoje=hoje)

        assert avaliacao.prints[0].tipo == "image/jpeg"


class TestRotas:
    @pytest.fixture
    def app_com_chave(self, app):
        app.config["AVALIACOES_CHAVE"] = CHAVE
        return app

    def test_formulario_abre(self, client):
        resposta = client.get("/avaliacao")

        assert resposta.status_code == 200
        assert "O que você testou e funcionou" in resposta.get_data(as_text=True)

    def test_enviar_avaliacao_com_print(self, client, app):
        dados = dados_validos(data_teste=date.today().isoformat())
        dados["prints"] = [(io.BytesIO(PNG), "erro.png")]

        resposta = client.post("/avaliacao", data=dados, content_type="multipart/form-data")

        assert resposta.status_code == 302
        assert resposta.headers["Location"].endswith("/avaliacao/obrigado")
        assert Avaliacao.query.count() == 1
        assert PrintAvaliacao.query.count() == 1

    def test_enviar_sem_nome_mostra_erro_e_mantem_o_texto(self, client, app):
        dados = dados_validos(nome="", data_teste=date.today().isoformat(), funcionou="Texto que não pode sumir")

        resposta = client.post("/avaliacao", data=dados)

        assert resposta.status_code == 400
        html = resposta.get_data(as_text=True)
        assert "Informe o seu nome." in html
        assert "Texto que não pode sumir" in html

    def test_resultados_sem_chave_configurada_nao_existem(self, client, app):
        app.config["AVALIACOES_CHAVE"] = None

        assert client.get("/avaliacoes?chave=qualquer").status_code == 404

    def test_resultados_com_chave_errada(self, client, app_com_chave):
        assert client.get("/avaliacoes?chave=errada").status_code == 404
        assert client.get("/avaliacoes").status_code == 404

    def test_resultados_com_chave_certa(self, client, app_com_chave, hoje):
        avaliacoes.criar_avaliacao(dados_validos(), [("tela.png", PNG)], hoje=hoje)

        resposta = client.get(f"/avaliacoes?chave={CHAVE}")

        assert resposta.status_code == 200
        html = resposta.get_data(as_text=True)
        assert "Maria Souza" in html
        assert "Colocar busca de tarefas." in html

    def test_resultados_em_json(self, client, app_com_chave, hoje):
        avaliacoes.criar_avaliacao(dados_validos(), [("tela.png", PNG)], hoje=hoje)

        dados = client.get(f"/avaliacoes.json?chave={CHAVE}").get_json()

        assert dados[0]["nome"] == "Maria Souza"
        assert dados[0]["data_teste"] == "2026-10-20"
        assert len(dados[0]["prints"]) == 1

    def test_ver_print_exige_chave(self, client, app_com_chave, hoje):
        avaliacao = avaliacoes.criar_avaliacao(dados_validos(), [("tela.png", PNG)], hoje=hoje)
        print_id = avaliacao.prints[0].id

        assert client.get(f"/avaliacoes/prints/{print_id}").status_code == 404
        resposta = client.get(f"/avaliacoes/prints/{print_id}?chave={CHAVE}")
        assert resposta.status_code == 200
        assert resposta.mimetype == "image/png"
        assert resposta.data == PNG
        assert resposta.headers["X-Content-Type-Options"] == "nosniff"
