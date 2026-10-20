"""Tratamento de erros: o usuário vê sempre uma mensagem clara, nunca o erro técnico."""
from flask import jsonify, render_template
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from app.controllers.respostas import quer_json
from app.models import db
from app.models.erros import ErroNaoEncontrado

MSG_ERRO_GERAL = "Algo deu errado. Tente novamente em instantes."


def _responder(mensagem, status):
    if quer_json():
        return jsonify(mensagem=mensagem), status
    return render_template("erro.html", mensagem=mensagem, status=status), status


def registrar(app):
    @app.errorhandler(ErroNaoEncontrado)
    def nao_encontrado(erro):
        return _responder(erro.mensagem, 404)

    @app.errorhandler(404)
    def pagina_inexistente(_erro):
        return _responder("Página não encontrada.", 404)

    @app.errorhandler(413)
    def envio_grande_demais(_erro):
        return _responder("Os arquivos enviados são grandes demais. Envie prints de até 3 MB cada.", 413)

    @app.errorhandler(405)
    def metodo_nao_permitido(_erro):
        return _responder("Essa ação não é permitida por aqui.", 405)

    @app.errorhandler(SQLAlchemyError)
    def erro_de_banco(erro):
        db.session.rollback()
        app.logger.exception("Erro no banco de dados: %s", erro)
        return _responder(MSG_ERRO_GERAL, 500)

    @app.errorhandler(Exception)
    def erro_inesperado(erro):
        if isinstance(erro, HTTPException):
            return _responder(erro.description, erro.code)
        app.logger.exception("Erro inesperado: %s", erro)
        return _responder(MSG_ERRO_GERAL, 500)
