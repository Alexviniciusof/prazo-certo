"""Configuração compartilhada dos testes.

Cada teste recebe uma aplicação nova com um banco SQLite em memória,
então um teste nunca interfere no outro.
"""
from datetime import date

import pytest

from app import create_app
from app.models import db

HOJE = date(2026, 10, 20)


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def hoje():
    return HOJE
