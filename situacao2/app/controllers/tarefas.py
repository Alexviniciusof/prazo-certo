"""Controller de tarefas."""
from datetime import date

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.controllers.respostas import quer_json
from app.models import servicos
from app.models.erros import ErroValidacao

bp = Blueprint("tarefas", __name__, url_prefix="/tarefas")


@bp.get("/atrasadas")
def atrasadas():
    hoje = date.today()
    tarefas = servicos.listar_tarefas_atrasadas(hoje=hoje)
    return render_template("tarefas/atrasadas.html", tarefas=tarefas, hoje=hoje)


@bp.get("/<int:tarefa_id>/editar")
def editar(tarefa_id):
    tarefa = servicos.obter_tarefa(tarefa_id)
    dados = {"titulo": tarefa.titulo, "prazo": tarefa.prazo.isoformat() if tarefa.prazo else ""}
    return render_template("tarefas/form.html", tarefa=tarefa, dados=dados)


@bp.post("/<int:tarefa_id>/editar")
def atualizar(tarefa_id):
    dados = request.form
    try:
        tarefa = servicos.editar_tarefa(tarefa_id, dados.get("titulo"), dados.get("prazo"))
    except ErroValidacao as erro:
        tarefa = servicos.obter_tarefa(tarefa_id)
        return render_template("tarefas/form.html", tarefa=tarefa, dados=dados, erro=erro.mensagem), 400
    flash("Tarefa atualizada com sucesso.", "sucesso")
    return redirect(url_for("projetos.detalhar", projeto_id=tarefa.projeto_id))


@bp.post("/<int:tarefa_id>/alternar")
def alternar(tarefa_id):
    tarefa = servicos.alternar_tarefa(tarefa_id)
    mensagem = "Tarefa marcada como concluída." if tarefa.concluida else "Tarefa marcada como pendente."
    if quer_json():
        projeto = tarefa.projeto
        hoje = date.today()
        return jsonify(
            id=tarefa.id,
            status=tarefa.status,
            concluida=tarefa.concluida,
            atrasada=tarefa.esta_atrasada(hoje),
            progresso=projeto.progresso,
            total=projeto.total_tarefas,
            concluidas=projeto.tarefas_concluidas,
            atrasadas=projeto.total_atrasadas(hoje),
            mensagem=mensagem,
        )
    flash(mensagem, "sucesso")
    return redirect(request.form.get("voltar_para") or url_for("projetos.detalhar", projeto_id=tarefa.projeto_id))


@bp.post("/<int:tarefa_id>/excluir")
def excluir(tarefa_id):
    tarefa = servicos.obter_tarefa(tarefa_id)
    projeto_id = tarefa.projeto_id
    servicos.excluir_tarefa(tarefa_id)
    flash("Tarefa excluída.", "sucesso")
    return redirect(url_for("projetos.detalhar", projeto_id=projeto_id))
