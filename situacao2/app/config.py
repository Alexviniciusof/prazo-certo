"""Configurações da aplicação, lidas de variáveis de ambiente (arquivo .env).

Nenhuma senha ou chave fica no código: SECRET_KEY e DATABASE_URL vêm do ambiente.
"""
import os
import secrets
from pathlib import Path

PASTA_INSTANCIA = Path(__file__).resolve().parent.parent / "instance"


def normalizar_url_do_banco(url):
    """Ajusta o endereço do PostgreSQL para usar o driver psycopg (versão 3).

    Serviços de hospedagem (como o Render) entregam "postgres://..." ou "postgresql://...";
    o SQLAlchemy precisa de "postgresql+psycopg://..." para usar o driver instalado.
    """
    for prefixo in ("postgres://", "postgresql://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg://" + url[len(prefixo):]
    return url


def _url_do_banco(padrao):
    return normalizar_url_do_banco(os.environ.get("DATABASE_URL") or padrao)


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Limite do envio do formulário de avaliação (3 prints de até 3 MB + textos).
    MAX_CONTENT_LENGTH = 12 * 1024 * 1024
    TESTING = False
    DEBUG = False

    def __init__(self):
        self.SECRET_KEY = os.environ.get("SECRET_KEY")
        # Chave para ver as avaliações dos colegas em /avaliacoes?chave=...
        # Sem ela, a página de resultados fica desligada.
        self.AVALIACOES_CHAVE = os.environ.get("AVALIACOES_CHAVE") or None
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
        # Por padrão os testes usam SQLite em memória. Para rodá-los no PostgreSQL,
        # defina TEST_DATABASE_URL apontando para um banco vazio de testes.
        self.SQLALCHEMY_DATABASE_URI = normalizar_url_do_banco(
            os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory:"
        )


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
