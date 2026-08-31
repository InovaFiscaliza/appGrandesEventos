(() => {
  const tabela = document.querySelector("#auditoria-tabela");
  const paginacao = document.querySelector("#auditoria-pagination");
  const seletorTamanho = document.querySelector("#auditoria-page-size");
  if (!tabela || !paginacao || !seletorTamanho) return;

  const linhas = Array.from(tabela.querySelectorAll("tbody tr"));
  let tamanhoPagina = Number(seletorTamanho.value) || 20;
  let paginaAtual = 1;

  function criarBotao(texto, pagina, desabilitado = false, atual = false) {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.textContent = texto;
    botao.disabled = desabilitado;
    if (atual) {
      botao.classList.add("pagina-atual");
      botao.setAttribute("aria-current", "page");
    }
    botao.addEventListener("click", () => {
      paginaAtual = pagina;
      renderizar();
    });
    paginacao.appendChild(botao);
  }

  function criarSeparador() {
    const separador = document.createElement("span");
    separador.textContent = "…";
    separador.setAttribute("aria-hidden", "true");
    paginacao.appendChild(separador);
  }

  function paginasVisiveis(totalPaginas) {
    if (totalPaginas <= 7) {
      return Array.from({ length: totalPaginas }, (_, indice) => indice + 1);
    }

    const paginas = new Set([
      1,
      2,
      totalPaginas - 1,
      totalPaginas,
      paginaAtual - 1,
      paginaAtual,
      paginaAtual + 1,
    ]);
    return Array.from(paginas)
      .filter((pagina) => pagina >= 1 && pagina <= totalPaginas)
      .sort((a, b) => a - b);
  }

  function renderizarPaginacao(totalPaginas) {
    paginacao.replaceChildren();
    if (linhas.length <= tamanhoPagina) {
      paginacao.hidden = true;
      return;
    }

    paginacao.hidden = false;
    criarBotao("«", 1, paginaAtual === 1);
    criarBotao("‹", Math.max(1, paginaAtual - 1), paginaAtual === 1);

    let paginaAnterior = 0;
    paginasVisiveis(totalPaginas).forEach((pagina) => {
      if (paginaAnterior && pagina - paginaAnterior > 1) criarSeparador();
      criarBotao(String(pagina), pagina, false, pagina === paginaAtual);
      paginaAnterior = pagina;
    });

    criarBotao(
      "›",
      Math.min(totalPaginas, paginaAtual + 1),
      paginaAtual === totalPaginas
    );
    criarBotao("»", totalPaginas, paginaAtual === totalPaginas);
  }

  function renderizar() {
    const totalPaginas = Math.max(1, Math.ceil(linhas.length / tamanhoPagina));
    paginaAtual = Math.min(paginaAtual, totalPaginas);
    const inicio = (paginaAtual - 1) * tamanhoPagina;

    linhas.forEach((linha, indice) => {
      linha.hidden = indice < inicio || indice >= inicio + tamanhoPagina;
    });
    renderizarPaginacao(totalPaginas);
  }

  seletorTamanho.addEventListener("change", () => {
    tamanhoPagina = Number(seletorTamanho.value) || 20;
    paginaAtual = 1;
    renderizar();
  });

  renderizar();
})();
