// Prazo Certo — comportamento das telas (JavaScript puro).
// Tudo funciona sem JavaScript; aqui só melhoramos a experiência:
// confirmação antes de excluir, validação antes de enviar, contador de caracteres,
// mensagens que somem sozinhas e marcar tarefa como concluída sem recarregar a página.
(() => {
  "use strict";

  const caixaMensagens = document.getElementById("mensagens");
  const TEMPO_MENSAGEM = 4000;

  // ---------- mensagens ----------
  function prepararMensagem(elemento) {
    const fechar = document.createElement("button");
    fechar.type = "button";
    fechar.className = "mensagem-fechar";
    fechar.setAttribute("aria-label", "Fechar mensagem");
    fechar.textContent = "×";
    fechar.addEventListener("click", () => esconder(elemento));
    elemento.appendChild(fechar);
    if (elemento.classList.contains("mensagem-sucesso")) {
      setTimeout(() => esconder(elemento), TEMPO_MENSAGEM);
    }
  }

  function esconder(elemento) {
    elemento.classList.add("saindo");
    setTimeout(() => elemento.remove(), 300);
  }

  function mostrarMensagem(texto, tipo = "sucesso") {
    caixaMensagens.querySelectorAll(".mensagem").forEach((m) => m.remove());
    const p = document.createElement("p");
    p.className = `mensagem mensagem-${tipo}`;
    p.setAttribute("role", tipo === "erro" ? "alert" : "status");
    p.textContent = texto;
    caixaMensagens.appendChild(p);
    prepararMensagem(p);
  }

  caixaMensagens.querySelectorAll(".mensagem").forEach(prepararMensagem);

  // ---------- validação dos campos obrigatórios ----------
  function limparErro(campo) {
    campo.removeAttribute("aria-invalid");
    const aviso = document.getElementById(`${campo.id}-erro`);
    if (aviso) aviso.remove();
  }

  function mostrarErro(campo, texto) {
    limparErro(campo);
    campo.setAttribute("aria-invalid", "true");
    const aviso = document.createElement("p");
    aviso.id = `${campo.id}-erro`;
    aviso.className = "erro-campo";
    aviso.textContent = texto;
    campo.setAttribute("aria-describedby", aviso.id);
    campo.insertAdjacentElement("afterend", aviso);
  }

  function formularioValido(form) {
    let primeiroInvalido = null;
    form.querySelectorAll("[data-obrigatorio]").forEach((campo) => {
      if (campo.value.trim() === "") {
        mostrarErro(campo, campo.dataset.obrigatorio);
        primeiroInvalido = primeiroInvalido || campo;
      }
    });
    if (primeiroInvalido) primeiroInvalido.focus();
    return primeiroInvalido === null;
  }

  document.querySelectorAll("[data-obrigatorio]").forEach((campo) => {
    campo.addEventListener("input", () => limparErro(campo));
  });

  // O navegador aceitaria um campo só com espaços; nossa validação cuida disso e
  // mostra a mesma mensagem do servidor, então desligamos a validação nativa.
  document.querySelectorAll("form").forEach((form) => {
    if (form.querySelector("[data-obrigatorio]")) form.noValidate = true;
  });

  // ---------- contador de caracteres ----------
  document.querySelectorAll("[data-contador]").forEach((campo) => {
    const contador = document.createElement("p");
    contador.className = "contador";
    contador.setAttribute("aria-live", "polite");
    const atualizar = () => {
      contador.textContent = `${campo.value.length} de ${campo.maxLength} caracteres`;
    };
    campo.insertAdjacentElement("afterend", contador);
    campo.addEventListener("input", atualizar);
    atualizar();
  });

  // ---------- aviso de prazo que já passou (antes de salvar) ----------
  document.querySelectorAll("input[type=date][data-hoje]").forEach((campo) => {
    const dica = document.createElement("p");
    dica.className = "dica-prazo";
    dica.setAttribute("aria-live", "polite");
    const atualizar = () => {
      // Datas no formato AAAA-MM-DD podem ser comparadas como texto.
      const passou = campo.value !== "" && campo.value < campo.dataset.hoje;
      dica.textContent = passou ? "Esse prazo já passou: a tarefa vai aparecer como atrasada." : "";
      dica.hidden = !passou;
    };
    campo.insertAdjacentElement("afterend", dica);
    campo.addEventListener("input", atualizar);
    campo.addEventListener("change", atualizar);
    atualizar();
  });

  // ---------- ordem da lista: aplica assim que o usuário escolhe ----------
  document.querySelectorAll("[data-enviar-ao-mudar]").forEach((campo) => {
    campo.addEventListener("change", () => campo.form.submit());
  });

  // ---------- concluir / reabrir tarefa sem recarregar ----------
  function atualizarResumo(dados) {
    const resumo = document.getElementById("resumo-projeto");
    if (!resumo) return;
    const barra = resumo.querySelector("[data-barra]");
    barra.setAttribute("aria-valuenow", dados.progresso);
    barra.querySelector(".progresso-barra").style.width = `${dados.progresso}%`;
    resumo.querySelector("[data-progresso]").textContent = `${dados.progresso}%`;
    resumo.querySelector("[data-contagem]").textContent = `${dados.concluidas} de ${dados.total}`;
    resumo.querySelector("[data-atrasadas]").textContent =
      `${dados.atrasadas} atrasada${dados.atrasadas === 1 ? "" : "s"}`;
  }

  function removerDaLista(item) {
    const lista = item.parentElement;
    item.classList.add("removendo");
    setTimeout(() => {
      item.remove();
      if (!lista.children.length) {
        const vazio = document.createElement("p");
        vazio.className = "cartao vazio";
        vazio.textContent = lista.dataset.vazio;
        lista.replaceWith(vazio);
      }
    }, 300);
  }

  async function alternarTarefa(form) {
    const item = form.closest(".tarefa");
    const botao = form.querySelector("button");
    botao.disabled = true;
    try {
      const resposta = await fetch(form.action, {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new FormData(form),
      });
      const dados = await resposta.json().catch(() => ({}));
      if (!resposta.ok) {
        mostrarMensagem(dados.mensagem || "Não foi possível atualizar a tarefa. Tente novamente.", "erro");
        return;
      }
      item.classList.toggle("concluida", dados.concluida);
      item.classList.toggle("atrasada", dados.atrasada);
      botao.setAttribute("aria-pressed", String(dados.concluida));
      botao.setAttribute("aria-label", dados.concluida ? "Marcar como pendente" : "Marcar como concluída");
      atualizarResumo(dados);
      mostrarMensagem(dados.mensagem);
      if (dados.concluida && item.parentElement.hasAttribute("data-remover-concluidas")) {
        removerDaLista(item);
      }
    } catch {
      mostrarMensagem("Sem conexão com o servidor. Verifique a internet e tente novamente.", "erro");
    } finally {
      botao.disabled = false;
    }
  }

  // ---------- envio dos formulários ----------
  document.addEventListener("submit", (evento) => {
    const form = evento.target;

    if (form.dataset.confirmar && !window.confirm(form.dataset.confirmar)) {
      evento.preventDefault();
      return;
    }
    if (!formularioValido(form)) {
      evento.preventDefault();
      return;
    }
    if (form.classList.contains("form-alternar") && window.fetch) {
      evento.preventDefault();
      alternarTarefa(form);
      return;
    }
    // Evita envio duplicado com clique duplo.
    const botao = form.querySelector('button[type="submit"]');
    if (botao) setTimeout(() => { botao.disabled = true; }, 0);
  });
})();

// Ao voltar para a página pelo botão "Voltar" do navegador, reativa os botões.
window.addEventListener("pageshow", () => {
  document.querySelectorAll('button[type="submit"][disabled]').forEach((b) => { b.disabled = false; });
});

// Prints no formulário de avaliação: reduz cada imagem no navegador (até 1600 px, JPEG)
// para caber no limite de envio, e mostra a prévia.
(() => {
  const campo = document.querySelector("input[type=file][data-max-arquivos]");
  if (!campo) return;
  const previas = document.getElementById("previas");
  const maxArquivos = Number(campo.dataset.maxArquivos);
  const maxBytes = Number(campo.dataset.maxMb) * 1024 * 1024;
  const LADO_MAXIMO = 1600;

  function carregarImagem(arquivo) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => { URL.revokeObjectURL(img.src); resolve(img); };
      img.onerror = () => reject(new Error("imagem inválida"));
      img.src = URL.createObjectURL(arquivo);
    });
  }

  async function reduzir(arquivo) {
    if (arquivo.size <= maxBytes && arquivo.type !== "image/png") return arquivo;
    const img = await carregarImagem(arquivo);
    const escala = Math.min(1, LADO_MAXIMO / Math.max(img.width, img.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(img.width * escala);
    canvas.height = Math.round(img.height * escala);
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    for (const qualidade of [0.85, 0.7, 0.55, 0.4]) {
      const blob = await new Promise((r) => canvas.toBlob(r, "image/jpeg", qualidade));
      if (blob && blob.size <= maxBytes) {
        const nome = arquivo.name.replace(/\.[^.]+$/, "") + ".jpg";
        return new File([blob], nome, { type: "image/jpeg" });
      }
    }
    throw new Error(`A imagem “${arquivo.name}” é grande demais mesmo reduzida.`);
  }

  function avisar(texto) {
    const aviso = document.createElement("p");
    aviso.className = "erro-campo";
    aviso.textContent = texto;
    previas.appendChild(aviso);
  }

  campo.addEventListener("change", async () => {
    previas.replaceChildren();
    const arquivos = [...campo.files];
    if (arquivos.length > maxArquivos) {
      campo.value = "";
      avisar(`Escolha no máximo ${maxArquivos} imagens.`);
      return;
    }
    const botao = campo.form.querySelector('button[type="submit"]');
    botao.disabled = true;
    try {
      const reduzidos = await Promise.all(arquivos.map(reduzir));
      const transferencia = new DataTransfer();
      reduzidos.forEach((arquivo) => transferencia.items.add(arquivo));
      campo.files = transferencia.files;
      reduzidos.forEach((arquivo) => {
        const img = document.createElement("img");
        img.alt = arquivo.name;
        img.src = URL.createObjectURL(arquivo);
        img.onload = () => URL.revokeObjectURL(img.src);
        previas.appendChild(img);
      });
    } catch (erro) {
      campo.value = "";
      avisar(erro.message.startsWith("A imagem") ? erro.message : "Não foi possível ler uma das imagens. Tente outra.");
    } finally {
      botao.disabled = false;
    }
  });
})();
