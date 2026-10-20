"""Funções de apoio usadas pelos controllers."""
from flask import request


def quer_json():
    """True quando a requisição veio do JavaScript pedindo JSON."""
    return request.accept_mimetypes.best == "application/json"
