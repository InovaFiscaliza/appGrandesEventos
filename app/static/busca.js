(() => {
  const campoBusca = document.querySelector("#busca-termo");
  const sugestoes = document.querySelector("#busca-sugestoes");
  const formularioBusca = campoBusca?.closest("form");
  let requisicaoSugestoes;

  function fecharSugestoes() {
    if (!sugestoes) return;
    sugestoes.replaceChildren();
    sugestoes.setAttribute("aria-expanded", "false");
  }

  function exibirSugestoes(itens) {
    if (!sugestoes) return;
    sugestoes.replaceChildren();
    itens.forEach((item) => {
      const botao = document.createElement("button");
      botao.type = "button";
      botao.className = "busca-sugestao";
      botao.setAttribute("role", "option");
      botao.innerHTML = `<strong>ID ${item.id}</strong><span>${item.label}</span>`;
      botao.addEventListener("click", () => {
        campoBusca.value = item.id;
        fecharSugestoes();
        formularioBusca.requestSubmit();
      });
      sugestoes.appendChild(botao);
    });
    sugestoes.setAttribute("aria-expanded", String(itens.length > 0));
  }

  campoBusca?.addEventListener("input", async () => {
    const termo = campoBusca.value.trim();
    requisicaoSugestoes?.abort();
    if (!termo) {
      fecharSugestoes();
      return;
    }
    requisicaoSugestoes = new AbortController();
    try {
      const resposta = await fetch(
        `/api/busca/sugestoes?termo=${encodeURIComponent(termo)}`,
        { signal: requisicaoSugestoes.signal, cache: "no-store" }
      );
      if (!resposta.ok) throw new Error(`Falha HTTP ${resposta.status}`);
      exibirSugestoes(await resposta.json());
    } catch (erro) {
      if (erro.name !== "AbortError") fecharSugestoes();
    }
  });

  campoBusca?.addEventListener("keydown", (evento) => {
    if (evento.key === "Escape") fecharSugestoes();
  });
  document.addEventListener("click", (evento) => {
    if (!sugestoes?.contains(evento.target) && evento.target !== campoBusca) {
      fecharSugestoes();
    }
  });

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
