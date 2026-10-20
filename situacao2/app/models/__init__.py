"""Camada Model: tabelas do banco e regras de negócio."""
from app.models.banco import db
from app.models.projeto import Projeto
from app.models.tarefa import CONCLUIDA, PENDENTE, Tarefa

__all__ = ["db", "Projeto", "Tarefa", "PENDENTE", "CONCLUIDA"]
