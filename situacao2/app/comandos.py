"""Comandos de terminal da aplicação (flask --app run <comando>)."""
from datetime import date, timedelta

import click

from app.models import Projeto, db
from app.models import servicos


def registrar(app):
    @app.cli.command("popular-exemplo")
    def popular_exemplo():
        """Cria projetos e tarefas de exemplo (para demonstração e para o vídeo)."""
        if Projeto.query.count():
            click.echo("O banco já tem projetos. Nada foi criado.")
            return

        hoje = date.today()
        dia = lambda n: hoje + timedelta(days=n)  # noqa: E731

        tcc = servicos.criar_projeto("TCC", "Trabalho de conclusão do curso de Engenharia de Software.")
        for titulo, prazo, feita in [
            ("Definir o tema com o orientador", dia(-20), True),
            ("Escrever a introdução", dia(-6), True),
            ("Revisar a bibliografia", dia(-2), False),
            ("Montar o protótipo das telas", dia(3), False),
            ("Preparar a apresentação", dia(25), False),
        ]:
            tarefa = servicos.criar_tarefa(tcc.id, titulo, prazo)
            if feita:
                servicos.concluir_tarefa(tarefa.id)

        casa = servicos.criar_projeto("Mudança de casa", "Organizar a mudança para o apartamento novo.")
        for titulo, prazo, feita in [
            ("Contratar o caminhão", dia(-1), False),
            ("Encaixotar os livros", dia(5), False),
            ("Transferir a internet", None, False),
            ("Pedir orçamento de pintura", dia(-10), True),
        ]:
            tarefa = servicos.criar_tarefa(casa.id, titulo, prazo)
            if feita:
                servicos.concluir_tarefa(tarefa.id)

        servicos.criar_projeto("Viagem de férias")
        db.session.commit()
        click.echo("Pronto: 3 projetos de exemplo criados.")
