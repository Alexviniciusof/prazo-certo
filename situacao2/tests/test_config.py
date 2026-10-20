"""Configuração lida do ambiente."""
import pytest

from app import create_app
from app.config import normalizar_url_do_banco


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("postgres://u:s@host:5432/db", "postgresql+psycopg://u:s@host:5432/db"),
        ("postgresql://u:s@host:5432/db", "postgresql+psycopg://u:s@host:5432/db"),
        ("postgresql+psycopg://u:s@host/db", "postgresql+psycopg://u:s@host/db"),
        ("mysql+pymysql://u:s@host/db", "mysql+pymysql://u:s@host/db"),
        ("sqlite:///arquivo.db", "sqlite:///arquivo.db"),
    ],
)
def test_normaliza_endereco_do_banco(entrada, esperado):
    assert normalizar_url_do_banco(entrada) == esperado


def test_producao_exige_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setattr("app.load_dotenv", lambda: None)

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")
