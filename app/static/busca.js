(() => {
  const tabela = document.querySelector(".busca-table");
  const paginacao = document.querySelector("#busca-pagination");
  const seletorTamanho = document.querySelector("#busca-page-size");
  if (!tabela || !paginacao || !seletorTamanho) return;

  const linhas = Array.from(tabela.querySelectorAll("tbody tr"));
  let tamanhoPagina = Number(seletorTamanho.value) || 20;
  let paginaAtual = 1;

  function criarBotao(texto, pagina, desabilitado = false, atual = false) {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.textContent = texto;
    botao.disabled = desabilitado;
    if (atual) botao.classList.add("pagina-atual");
    botao.addEventListener("click", () => {
      paginaAtual = pagina;
      renderizar();
    });
    paginacao.appendChild(botao);
  }

  function renderizar() {
    const totalPaginas = Math.max(1, Math.ceil(linhas.length / tamanhoPagina));
    paginaAtual = Math.min(paginaAtual, totalPaginas);
    const inicio = (paginaAtual - 1) * tamanhoPagina;
    linhas.forEach((linha, indice) => {
      linha.hidden = indice < inicio || indice >= inicio + tamanhoPagina;
    });
    paginacao.replaceChildren();
    if (linhas.length <= tamanhoPagina) {
      paginacao.hidden = true;
      return;
    }
    paginacao.hidden = false;
    criarBotao("«", 1, paginaAtual === 1);
    criarBotao("‹", Math.max(1, paginaAtual - 1), paginaAtual === 1);
    for (let pagina = 1; pagina <= totalPaginas; pagina += 1) {
      criarBotao(String(pagina), pagina, false, pagina === paginaAtual);
    }
    criarBotao("›", Math.min(totalPaginas, paginaAtual + 1), paginaAtual === totalPaginas);
    criarBotao("»", totalPaginas, paginaAtual === totalPaginas);
  }

  seletorTamanho.addEventListener("change", () => {
    tamanhoPagina = Number(seletorTamanho.value) || 20;
    paginaAtual = 1;
    renderizar();
  });
  renderizar();
})();
