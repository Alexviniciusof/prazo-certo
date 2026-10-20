"""Configurações da aplicação, lidas de variáveis de ambiente (arquivo .env).

Nenhuma senha ou chave fica no código: SECRET_KEY e DATABASE_URL vêm do ambiente.
"""
import os
import secrets
from pathlib import Path

PASTA_INSTANCIA = Path(__file__).resolve().parent.parent / "instance"


def _url_do_banco(padrao):
    url = os.environ.get("DATABASE_URL") or padrao
    # Alguns serviços de hospedagem entregam "postgres://", que o SQLAlchemy não aceita.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False
    DEBUG = False

    def __init__(self):
        self.SECRET_KEY = os.environ.get("SECRET_KEY")
        self.SQLALCHEMY_DATABASE_URI = _url_do_banco(f"sqlite:///{PASTA_INSTANCIA / 'prazo_certo.db'}")


class DevelopmentConfig(Config):
    DEBUG = True

    def __init__(self):
        super().__init__()
        # Em desenvolvimento, sem SECRET_KEY no .env, gera uma chave aleatória a cada execução.
        self.SECRET_KEY = self.SECRET_KEY or secrets.token_hex(32)


class TestingConfig(Config):
    TESTING = True

    def __init__(self):
        super().__init__()
        self.SECRET_KEY = "chave-usada-somente-nos-testes"
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    def __init__(self):
        super().__init__()
        if not self.SECRET_KEY:
            raise RuntimeError("Defina a variável de ambiente SECRET_KEY antes de rodar em produção.")


CONFIGURACOES = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
