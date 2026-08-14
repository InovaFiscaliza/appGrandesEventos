(() => {
  function inicializar() {
  const palavrasSalvar = /\b(salvar|registrar|cadastrar|criar|inserir)\b/i;
  const palavrasExcluir = /\b(excluir|apagar)\b/i;
  const confirmacoesLiberadas = new WeakSet();
  let elementoFoco;

  const dialogo = document.createElement("div");
  dialogo.className = "confirmacao-overlay";
  dialogo.hidden = true;
  dialogo.innerHTML = `
    <section class="confirmacao-dialogo" role="dialog" aria-modal="true"
             aria-labelledby="confirmacao-titulo" aria-describedby="confirmacao-mensagem">
      <h2 id="confirmacao-titulo">Confirmar ação</h2>
      <p id="confirmacao-mensagem"></p>
      <div class="confirmacao-acoes">
        <button type="button" class="btn btn-submit confirmacao-confirmar">Confirmar</button>
        <button type="button" class="btn confirmacao-cancelar">Cancelar</button>
      </div>
    </section>
  `;
  document.body.appendChild(dialogo);

  const mensagemElemento = dialogo.querySelector("#confirmacao-mensagem");
  const botaoCancelar = dialogo.querySelector(".confirmacao-cancelar");
  const botaoConfirmar = dialogo.querySelector(".confirmacao-confirmar");

  function fechar() {
    dialogo.hidden = true;
    document.body.classList.remove("confirmacao-aberta");
    elementoFoco?.focus();
  }

  function abrir(mensagem, continuar, elemento) {
    elementoFoco = elemento;
    mensagemElemento.textContent = mensagem;
    dialogo.hidden = false;
    document.body.classList.add("confirmacao-aberta");
    botaoConfirmar.focus();

    const confirmar = () => {
      fechar();
      continuar();
    };
    botaoConfirmar.onclick = confirmar;
    botaoCancelar.onclick = fechar;
  }

  window.confirmarExclusaoImagem = (continuar, elemento) => {
    abrir("Confirma a exclusão desta imagem?", continuar, elemento);
  };

  function mensagemPara(botao) {
    const formulario = botao?.form;
    const destino = formulario?.getAttribute("action") || botao?.getAttribute("href") || "";
    const texto = [
      botao?.textContent,
      botao?.getAttribute("aria-label"),
      botao?.getAttribute("title"),
    ].filter(Boolean).join(" ");
    if (palavrasExcluir.test(texto) || /\/excluir(?:$|[/?#])/i.test(destino)) {
      return "Confirma a exclusão deste registro?";
    }
    if (palavrasSalvar.test(texto) || /\/editar(?:$|[/?#])/i.test(destino)) {
      return "Confirma o salvamento deste registro?";
    }
    return "";
  }

  document.addEventListener("submit", (evento) => {
    const mensagem = mensagemPara(evento.submitter);
    if (!mensagem || confirmacoesLiberadas.has(evento.target)) return;
    evento.preventDefault();
    evento.stopImmediatePropagation();
    abrir(mensagem, () => {
      confirmacoesLiberadas.add(evento.target);
      evento.target.requestSubmit(evento.submitter);
      confirmacoesLiberadas.delete(evento.target);
    }, evento.submitter);
  }, true);

  document.addEventListener("click", (evento) => {
    const botao = evento.target.closest("button, a");
    if (!botao || botao.tagName === "BUTTON" && botao.type === "submit") return;
    if (botao.tagName === "A") return;
    if (botao.hasAttribute("data-confirmacao-imagem")) return;
    if (confirmacoesLiberadas.has(botao)) return;
    const mensagem = mensagemPara(botao);
    if (!mensagem) return;
    evento.preventDefault();
    evento.stopImmediatePropagation();
    abrir(mensagem, () => {
      confirmacoesLiberadas.add(botao);
      botao.click();
      confirmacoesLiberadas.delete(botao);
    }, botao);
  }, true);

  document.addEventListener("keydown", (evento) => {
    if (dialogo.hidden) return;
    if (evento.key === "Escape") {
      evento.preventDefault();
      fechar();
    }
    if (evento.key === "Tab") {
      evento.preventDefault();
      (document.activeElement === botaoConfirmar ? botaoCancelar : botaoConfirmar).focus();
    }
  });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inicializar, { once: true });
  } else {
    inicializar();
  }
})();