"""Controller do formulário de avaliação usado pelos colegas (Situação 3)."""
import hmac
from datetime import date

from flask import Blueprint, abort, current_app, jsonify, make_response, redirect, render_template, request, url_for

from app.models import servicos_avaliacao
from app.models.erros import ErroValidacao

bp = Blueprint("avaliacoes", __name__)


def _exigir_chave():
    """A lista de avaliações só abre com a chave certa; sem ela, a página 'não existe'."""
    esperada = current_app.config.get("AVALIACOES_CHAVE")
    informada = request.args.get("chave", "")
    if not esperada or not hmac.compare_digest(informada.encode(), esperada.encode()):
        abort(404)
    return informada


@bp.get("/avaliacao")
def formulario():
    return render_template("avaliacoes/form.html", dados={"data_teste": date.today().isoformat()})


@bp.post("/avaliacao")
def enviar():
    arquivos = [(arquivo.filename, arquivo.read()) for arquivo in request.files.getlist("prints")]
    try:
        servicos_avaliacao.criar_avaliacao(request.form, arquivos)
    except ErroValidacao as erro:
        return render_template("avaliacoes/form.html", dados=request.form, erro=erro.mensagem), 400
    return redirect(url_for("avaliacoes.obrigado"))


@bp.get("/avaliacao/obrigado")
def obrigado():
    return render_template("avaliacoes/obrigado.html")


@bp.get("/avaliacoes")
def resultados():
    chave = _exigir_chave()
    return render_template(
        "avaliacoes/resultados.html", avaliacoes=servicos_avaliacao.listar_avaliacoes(), chave=chave
    )


@bp.get("/avaliacoes.json")
def resultados_json():
    chave = _exigir_chave()
    return jsonify([
        {
            "id": a.id,
            "nome": a.nome,
            "data_teste": a.data_teste.isoformat(),
            "dispositivo": a.dispositivo,
            "funcionou": a.funcionou,
            "nao_funcionou": a.nao_funcionou,
            "nao_testado": a.nao_testado,
            "sugestoes": a.sugestoes,
            "nota": a.nota,
            "enviado_em": a.criado_em.isoformat(timespec="minutes"),
            "prints": [
                {
                    "nome_arquivo": p.nome_arquivo,
                    "url": url_for("avaliacoes.ver_print", print_id=p.id, chave=chave, _external=True),
                }
                for p in a.prints
            ],
        }
        for a in servicos_avaliacao.listar_avaliacoes()
    ])


@bp.get("/avaliacoes/prints/<int:print_id>")
def ver_print(print_id):
    _exigir_chave()
    imagem = servicos_avaliacao.obter_print(print_id)
    resposta = make_response(imagem.conteudo)
    resposta.mimetype = imagem.tipo
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["Content-Security-Policy"] = "default-src 'none'"
    return resposta
