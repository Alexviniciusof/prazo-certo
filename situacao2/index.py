"""Ponto de entrada usado pela Vercel (ela procura uma variável `app` neste arquivo)."""
from app import create_app

app = create_app()
