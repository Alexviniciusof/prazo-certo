"""Filtros usados nos templates."""


def registrar(app):
    @app.template_filter("data_br")
    def data_br(valor):
        return valor.strftime("%d/%m/%Y") if valor else ""
