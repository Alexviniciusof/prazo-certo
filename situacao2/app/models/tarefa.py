"""Model Tarefa."""
from datetime import date, datetime

from app.models.banco import db

PENDENTE = "pendente"
CONCLUIDA = "concluida"


class Tarefa(db.Model):
    __tablename__ = "tarefa"
    __table_args__ = (
        db.CheckConstraint(f"status IN ('{PENDENTE}', '{CONCLUIDA}')", name="ck_tarefa_status"),
        db.Index("ix_tarefa_status_prazo", "status", "prazo"),
    )

    TITULO_MAX = 150

    id = db.Column(db.Integer, primary_key=True)
    projeto_id = db.Column(
        db.Integer,
        db.ForeignKey("projeto.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    titulo = db.Column(db.String(TITULO_MAX), nullable=False)
    prazo = db.Column(db.Date)
    status = db.Column(db.String(10), nullable=False, default=PENDENTE)
    concluida_em = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)
    atualizado_em = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    projeto = db.relationship("Projeto", back_populates="tarefas")

    @property
    def concluida(self):
        return self.status == CONCLUIDA

    def concluir(self):
        self.status = CONCLUIDA
        self.concluida_em = datetime.now()

    def reabrir(self):
        self.status = PENDENTE
        self.concluida_em = None

    def esta_atrasada(self, hoje=None):
        """Atrasada = tem prazo, o prazo já passou e ainda está pendente."""
        hoje = hoje or date.today()
        return self.status == PENDENTE and self.prazo is not None and self.prazo < hoje

    def __repr__(self):
        return f"<Tarefa {self.id} {self.titulo!r}>"
