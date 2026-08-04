// Copiar texto de células ao clicar (delegação de evento)
(function () {
  function copiar(el) {
    const text = el.textContent.trim();
    function feedback() {
      const orig = el.textContent;
      el.textContent = "Copiado!";
      setTimeout(() => {
        el.textContent = orig;
      }, 1500);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(feedback, fallback);
    } else {
      fallback();
    }
    function fallback() {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      feedback();
    }
  }

  document.addEventListener("click", function (e) {
    const cell = e.target.closest(".copyable-cell");
    if (cell) copiar(cell);
  });
})();

(function () {
  const tabela = document.querySelector(".ute-table");
  const paginacao = document.querySelector("#ute-pagination");
  const seletorTamanho = document.querySelector("#ute-page-size");
  if (!tabela || !paginacao || !seletorTamanho) return;

  const linhas = Array.from(tabela.querySelectorAll("tbody tr"));
  let tamanhoPagina = Number(seletorTamanho.value) || 10;
  let paginaAtual = 1;

  function obterTotalPaginas() {
    return Math.max(1, Math.ceil(linhas.length / tamanhoPagina));
  }

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

  function renderizarPaginacao() {
    paginacao.innerHTML = "";
    if (linhas.length <= tamanhoPagina) {
      paginacao.hidden = true;
      return;
    }
    paginacao.hidden = false;
    const totalPaginas = obterTotalPaginas();
    criarBotao("«", 1, paginaAtual === 1);
    criarBotao("‹", Math.max(1, paginaAtual - 1), paginaAtual === 1);
    for (let pagina = 1; pagina <= totalPaginas; pagina += 1) {
      criarBotao(String(pagina), pagina, false, pagina === paginaAtual);
    }
    criarBotao("›", Math.min(totalPaginas, paginaAtual + 1), paginaAtual === totalPaginas);
    criarBotao("»", totalPaginas, paginaAtual === totalPaginas);
  }

  function renderizar() {
    const totalPaginas = obterTotalPaginas();
    paginaAtual = Math.min(paginaAtual, totalPaginas);
    const inicio = (paginaAtual - 1) * tamanhoPagina;
    linhas.forEach((linha, indice) => {
      linha.hidden = indice < inicio || indice >= inicio + tamanhoPagina;
    });
    renderizarPaginacao();
  }

  seletorTamanho.addEventListener("change", () => {
    tamanhoPagina = Number(seletorTamanho.value) || 10;
    paginaAtual = 1;
    renderizar();
  });

  renderizar();
})();
