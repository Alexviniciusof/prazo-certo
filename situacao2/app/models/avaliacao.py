"""Models da avaliação feita pelos colegas (Situação 3)."""
from datetime import datetime

from app.models.banco import db


class Avaliacao(db.Model):
    __tablename__ = "avaliacao"

    NOME_MAX = 100
    TEXTO_MAX = 2000
    DISPOSITIVO_MAX = 100

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(NOME_MAX), nullable=False)
    data_teste = db.Column(db.Date, nullable=False)
    dispositivo = db.Column(db.String(DISPOSITIVO_MAX))
    funcionou = db.Column(db.Text, nullable=False)
    nao_funcionou = db.Column(db.Text)
    nao_testado = db.Column(db.Text)
    sugestoes = db.Column(db.Text)
    nota = db.Column(db.Integer)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    prints = db.relationship(
        "PrintAvaliacao",
        back_populates="avaliacao",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="PrintAvaliacao.id",
    )

    __table_args__ = (
        db.CheckConstraint("nota IS NULL OR (nota BETWEEN 1 AND 5)", name="ck_avaliacao_nota"),
    )


class PrintAvaliacao(db.Model):
    """Captura de tela enviada junto com a avaliação."""

    __tablename__ = "avaliacao_print"

    id = db.Column(db.Integer, primary_key=True)
    avaliacao_id = db.Column(
        db.Integer, db.ForeignKey("avaliacao.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome_arquivo = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    conteudo = db.Column(db.LargeBinary, nullable=False)

    avaliacao = db.relationship("Avaliacao", back_populates="prints")
