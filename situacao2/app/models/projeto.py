"""Model Projeto."""
from datetime import datetime

from app.models.banco import db


class Projeto(db.Model):
    __tablename__ = "projeto"

    NOME_MAX = 100
    DESCRICAO_MAX = 500

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(NOME_MAX), nullable=False, unique=True)
    descricao = db.Column(db.String(DESCRICAO_MAX))
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)
    atualizado_em = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    tarefas = db.relationship(
        "Tarefa",
        back_populates="projeto",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def total_tarefas(self):
        return len(self.tarefas)

    @property
    def tarefas_concluidas(self):
        return sum(1 for tarefa in self.tarefas if tarefa.concluida)

    @property
    def progresso(self):
        """Porcentagem de tarefas concluídas (0 a 100). Projeto sem tarefas = 0."""
        if not self.tarefas:
            return 0
        return round(self.tarefas_concluidas * 100 / self.total_tarefas)

    def total_atrasadas(self, hoje=None):
        return sum(1 for tarefa in self.tarefas if tarefa.esta_atrasada(hoje))

    def __repr__(self):
        return f"<Projeto {self.id} {self.nome!r}>"
