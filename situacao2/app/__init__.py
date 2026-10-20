"""Prazo Certo — criação da aplicação Flask (padrão application factory)."""
import os

from dotenv import load_dotenv
from flask import Flask, redirect, url_for

from app.config import CONFIGURACOES, PASTA_INSTANCIA
from app.models import db


def create_app(nome_config=None):
    load_dotenv()
    nome_config = nome_config or os.environ.get("APP_ENV", "development")

    app = Flask(__name__, instance_path=str(PASTA_INSTANCIA))
    app.config.from_object(CONFIGURACOES[nome_config]())

    PASTA_INSTANCIA.mkdir(exist_ok=True)
    db.init_app(app)

    from app import comandos
    from app.controllers import erros, filtros, projetos, tarefas

    app.register_blueprint(projetos.bp)
    app.register_blueprint(tarefas.bp)
    erros.registrar(app)
    filtros.registrar(app)
    comandos.registrar(app)

    @app.get("/")
    def inicio():
        return redirect(url_for("projetos.listar"))

    with app.app_context():
        db.create_all()

    return app
