"""Funções de apoio usadas pelos controllers."""
from datetime import date

from flask import flash, request

AVISO_PRAZO_PASSADO = "Atenção: o prazo informado já passou, então a tarefa aparece como atrasada."


def quer_json():
    """True quando a requisição veio do JavaScript pedindo JSON."""
    return request.accept_mimetypes.best == "application/json"


def avisar_se_prazo_passou(tarefa):
    """Mostra um aviso (não bloqueia) quando a tarefa foi salva com um prazo que já passou."""
    if tarefa.esta_atrasada(date.today()):
        flash(AVISO_PRAZO_PASSADO, "aviso")
