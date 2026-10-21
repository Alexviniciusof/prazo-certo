"""Controller de projetos."""
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.respostas import avisar_se_prazo_passou
from app.models import servicos
from app.models.erros import ErroValidacao

bp = Blueprint("projetos", __name__, url_prefix="/projetos")


@bp.get("")
def listar():
    projetos = servicos.listar_projetos()
    return render_template("projetos/lista.html", projetos=projetos, hoje=date.today())


@bp.get("/novo")
def novo():
    return render_template("projetos/form.html", projeto=None, dados={})


@bp.post("")
def criar():
    dados = request.form
    try:
        projeto = servicos.criar_projeto(dados.get("nome"), dados.get("descricao"))
    except ErroValidacao as erro:
        return render_template("projetos/form.html", projeto=None, dados=dados, erro=erro.mensagem), 400
    flash("Projeto criado com sucesso.", "sucesso")
    return redirect(url_for("projetos.detalhar", projeto_id=projeto.id))


@bp.get("/<int:projeto_id>")
def detalhar(projeto_id):
    return _pagina_do_projeto(projeto_id)


@bp.get("/<int:projeto_id>/editar")
def editar(projeto_id):
    projeto = servicos.obter_projeto(projeto_id)
    dados = {"nome": projeto.nome, "descricao": projeto.descricao or ""}
    return render_template("projetos/form.html", projeto=projeto, dados=dados)


@bp.post("/<int:projeto_id>/editar")
def atualizar(projeto_id):
    dados = request.form
    try:
        servicos.editar_projeto(projeto_id, dados.get("nome"), dados.get("descricao"))
    except ErroValidacao as erro:
        projeto = servicos.obter_projeto(projeto_id)
        return render_template("projetos/form.html", projeto=projeto, dados=dados, erro=erro.mensagem), 400
    flash("Projeto atualizado com sucesso.", "sucesso")
    return redirect(url_for("projetos.detalhar", projeto_id=projeto_id))


@bp.post("/<int:projeto_id>/excluir")
def excluir(projeto_id):
    servicos.excluir_projeto(projeto_id)
    flash("Projeto e suas tarefas foram excluídos.", "sucesso")
    return redirect(url_for("projetos.listar"))


@bp.post("/<int:projeto_id>/tarefas")
def criar_tarefa(projeto_id):
    dados = request.form
    try:
        tarefa = servicos.criar_tarefa(projeto_id, dados.get("titulo"), dados.get("prazo"))
    except ErroValidacao as erro:
        return _pagina_do_projeto(projeto_id, dados_tarefa=dados, erro=erro.mensagem), 400
    flash("Tarefa criada com sucesso.", "sucesso")
    avisar_se_prazo_passou(tarefa)
    return redirect(url_for("projetos.detalhar", projeto_id=projeto_id))


def _pagina_do_projeto(projeto_id, dados_tarefa=None, erro=None):
    hoje = date.today()
    filtro = request.args.get("filtro", "todas")
    busca = request.args.get("busca", "").strip()
    ordem = request.args.get("ordem", servicos.ORDEM_PADRAO)
    if ordem not in servicos.ORDENS:
        ordem = servicos.ORDEM_PADRAO
    projeto = servicos.obter_projeto(projeto_id)
    tarefas = servicos.listar_tarefas(
        projeto_id, apenas_atrasadas=(filtro == "atrasadas"), hoje=hoje, busca=busca, ordem=ordem
    )
    return render_template(
        "projetos/detalhe.html",
        projeto=projeto,
        tarefas=tarefas,
        filtro=filtro,
        busca=busca,
        ordem=ordem,
        ordens=servicos.ORDENS,
        hoje=hoje,
        dados_tarefa=dados_tarefa or {},
        erro=erro,
    )
