"""Conexão com o banco de dados (SQLAlchemy)."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def _ligar_chaves_estrangeiras_no_sqlite(conexao, _registro):
    """O SQLite só respeita ON DELETE CASCADE com este PRAGMA ligado em cada conexão."""
    if type(conexao).__module__.startswith("sqlite3"):
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()
