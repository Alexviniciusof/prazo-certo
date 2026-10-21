"""Filtros e variáveis usados nos templates."""
from datetime import date


def registrar(app):
    @app.template_filter("data_br")
    def data_br(valor):
        return valor.strftime("%d/%m/%Y") if valor else ""

    @app.context_processor
    def datas():
        # Usado pelo JavaScript para avisar, antes de salvar, que o prazo escolhido já passou.
        return {"hoje_iso": date.today().isoformat()}
