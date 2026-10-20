"""Regras de negócio da avaliação feita pelos colegas."""
from datetime import date

from app.models.avaliacao import Avaliacao, PrintAvaliacao
from app.models.banco import db
from app.models.erros import ErroNaoEncontrado, ErroValidacao
from app.models.servicos import _converter_prazo, _texto_limpo, _transacao

MAX_PRINTS = 3
MAX_BYTES_PRINT = 3 * 1024 * 1024

# Tipo da imagem descoberto pelos primeiros bytes do arquivo (não confiamos no nome nem no navegador).
ASSINATURAS = (
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
)


def _tipo_da_imagem(conteudo):
    for assinatura, tipo in ASSINATURAS:
        if conteudo.startswith(assinatura):
            return tipo
    if conteudo[:4] == b"RIFF" and conteudo[8:12] == b"WEBP":
        return "image/webp"
    return None


def _obrigatorio(valor, mensagem, maximo, nome_do_campo):
    texto = _texto_limpo(valor)
    if not texto:
        raise ErroValidacao(mensagem)
    if len(texto) > maximo:
        raise ErroValidacao(f"O campo “{nome_do_campo}” pode ter no máximo {maximo} caracteres.")
    return texto


def _opcional(valor, maximo, nome_do_campo):
    texto = _texto_limpo(valor)
    if len(texto) > maximo:
        raise ErroValidacao(f"O campo “{nome_do_campo}” pode ter no máximo {maximo} caracteres.")
    return texto or None


def _validar_data(valor, hoje):
    data = _converter_prazo(valor) if valor else None
    if data is None:
        raise ErroValidacao("Informe a data do teste.")
    if data > hoje:
        raise ErroValidacao("A data do teste não pode estar no futuro.")
    return data


def _validar_nota(valor):
    if valor in (None, ""):
        return None
    try:
        nota = int(valor)
    except (TypeError, ValueError):
        nota = 0
    if not 1 <= nota <= 5:
        raise ErroValidacao("A nota deve ser de 1 a 5.")
    return nota


def _validar_prints(arquivos):
    """Recebe uma lista de (nome_do_arquivo, bytes). Arquivos vazios são ignorados."""
    arquivos = [(nome, conteudo) for nome, conteudo in arquivos or [] if conteudo]
    if len(arquivos) > MAX_PRINTS:
        raise ErroValidacao(f"Envie no máximo {MAX_PRINTS} prints.")
    prints = []
    for nome, conteudo in arquivos:
        if len(conteudo) > MAX_BYTES_PRINT:
            raise ErroValidacao(f"O print “{nome}” passa de 3 MB. Envie uma imagem menor.")
        tipo = _tipo_da_imagem(conteudo)
        if tipo is None:
            raise ErroValidacao(f"O arquivo “{nome}” não é uma imagem (use PNG, JPG, GIF ou WEBP).")
        prints.append(PrintAvaliacao(nome_arquivo=(nome or "print")[:255], tipo=tipo, conteudo=conteudo))
    return prints


def criar_avaliacao(dados, arquivos=None, hoje=None):
    """Valida e grava a avaliação. `dados` é um dicionário com os campos do formulário."""
    hoje = hoje or date.today()
    avaliacao = Avaliacao(
        nome=_obrigatorio(dados.get("nome"), "Informe o seu nome.", Avaliacao.NOME_MAX, "Nome"),
        data_teste=_validar_data(dados.get("data_teste"), hoje),
        dispositivo=_opcional(dados.get("dispositivo"), Avaliacao.DISPOSITIVO_MAX, "Aparelho e navegador"),
        funcionou=_obrigatorio(
            dados.get("funcionou"),
            "Conte o que você testou e funcionou.",
            Avaliacao.TEXTO_MAX,
            "O que testou e funcionou",
        ),
        nao_funcionou=_opcional(dados.get("nao_funcionou"), Avaliacao.TEXTO_MAX, "O que não funcionou"),
        nao_testado=_opcional(dados.get("nao_testado"), Avaliacao.TEXTO_MAX, "O que não foi testado"),
        sugestoes=_opcional(dados.get("sugestoes"), Avaliacao.TEXTO_MAX, "Sugestões"),
        nota=_validar_nota(dados.get("nota")),
    )
    avaliacao.prints = _validar_prints(arquivos)
    with _transacao():
        db.session.add(avaliacao)
    return avaliacao


def listar_avaliacoes():
    return Avaliacao.query.order_by(Avaliacao.criado_em, Avaliacao.id).all()


def obter_print(print_id):
    imagem = db.session.get(PrintAvaliacao, print_id)
    if imagem is None:
        raise ErroNaoEncontrado("Imagem não encontrada.")
    return imagem
