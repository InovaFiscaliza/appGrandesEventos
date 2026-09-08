// Aviso offline + interceptação de submit dos incidentes
(function () {
  const aviso = document.getElementById("offline-aviso-bsr");
  if (aviso) aviso.style.display = "none";

  const form = document.getElementById("form-bsr-erb");
  if (!form) return;

  const adicionar = document.getElementById("adicionar-fiscal-participante");
  const seletorArea = document.getElementById("seletor-fiscal-participante");
  const seletor = document.getElementById("fiscal-participante");
  const listaFiscais = document.getElementById("lista-fiscais-participantes");
  adicionar?.addEventListener("click", () => { seletorArea.hidden = false; seletor.focus(); });
  seletor?.addEventListener("change", () => {
    const opcao = seletor.selectedOptions[0];
    if (!opcao?.value || listaFiscais.querySelector(`[data-fiscal-id="${opcao.value}"]`)) return;
    const item = document.createElement("span");
    item.dataset.fiscalId = opcao.value;
    item.append(document.createTextNode(`${opcao.textContent} `));
    const remover = document.createElement("button");
    remover.type = "button"; remover.className = "fiscal-participante-remover"; remover.textContent = "×";
    remover.addEventListener("click", () => item.remove());
    const campo = document.createElement("input"); campo.type = "hidden"; campo.name = "fiscais_participantes"; campo.value = opcao.value;
    item.append(remover, campo); listaFiscais.appendChild(item); seletor.value = ""; seletorArea.hidden = true;
  });
  listaFiscais?.querySelectorAll("button").forEach((botao) => botao.addEventListener("click", () => botao.closest("span")?.remove()));

  document.querySelectorAll("[data-imagem-bsr-excluir]").forEach((botao) => {
    botao.addEventListener("click", () => {
      window.confirmarExclusaoImagem(async () => {
        botao.disabled = true;
        try {
          const resposta = await fetch(botao.dataset.imagemBsrExcluir, {
            method: "POST",
            headers: { Accept: "text/html" },
          });
          if (!resposta.ok) throw new Error(`Falha HTTP ${resposta.status}`);
          window.location.href = resposta.url;
        } catch (erro) {
          botao.disabled = false;
          alert("Não foi possível excluir a foto: " + erro.message);
        }
      }, botao);
    });
  });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    if (form.dataset.enviando === "1") return;
    form.dataset.enviando = "1";
    const botao = form.querySelector('button[type="submit"]');
    if (botao) botao.disabled = true;

    // Tenta enviar online primeiro
    const fd = new FormData(this);
    const destino = this.getAttribute("action") || "/bsr-erb";
    try {
      const resp = await fetch(destino, {
        method: "POST",
        body: fd,
      });
      if (resp.ok) {
        if (resp.redirected) {
          window.location.href = resp.url;
        } else {
          const html = await resp.text();
          document.open();
          document.write(html);
          document.close();
        }
        return;
      }
      // Se o servidor recusou, cai no offline
    } catch (_e) {
      // Falha de rede — continua para salvar offline
    }

    if (destino !== "/bsr-erb") {
      delete form.dataset.enviando;
      if (botao) botao.disabled = false;
      alert("Não é possível editar este registro sem conexão.");
      return;
    }

    const possuiFotos = fd.getAll("imagens").some((arquivo) => arquivo instanceof File && arquivo.size > 0);
    if (possuiFotos) {
      delete form.dataset.enviando;
      if (botao) botao.disabled = false;
      alert("As fotos precisam de conexão para serem enviadas. Mantenha o formulário aberto e tente novamente quando a conexão voltar.");
      return;
    }
    const dados = {
      tipo: fd.get("tipo") || "Bloqueador de sinal (BSR)",
      regiao: fd.get("regiao") || "",
      lat: fd.get("lat") || "",
      lon: fd.get("lon") || "",
      observacoes: fd.get("observacoes") || "",
      situacao: fd.get("situacao") || "Pendente",
      fiscais_participantes: fd.getAll("fiscais_participantes"),
    };

    if (!dados.regiao) {
      alert("O campo 'Local' é obrigatório.");
      return;
    }
    if (!dados.observacoes) {
      alert("O campo 'Observações' é obrigatório.");
      return;
    }

    try {
      await AppOffline.enfileirar("fila_bsr_erb", dados);
      const div = document.createElement("div");
      div.className = "flash flash-success";
      div.textContent = "📥 Salvo localmente. Será enviado ao reconectar.";
      this.parentElement.insertBefore(div, this);
      this.reset();
      delete form.dataset.enviando;
      if (botao) botao.disabled = false;
    } catch (err) {
      delete form.dataset.enviando;
      if (botao) botao.disabled = false;
      alert("Erro ao salvar localmente: " + err);
    }
  });
})();

(() => {
  const tabela = document.querySelector(".incidentes-lista table[data-paginacao]");
  const paginacao = document.querySelector(".incidentes-lista .pendencias-pagination");
  if (!tabela || !paginacao) return;
  const linhas = Array.from(tabela.querySelectorAll("tbody tr"));
  const tamanhoPagina = Number(tabela.dataset.paginacao) || 10;
  if (linhas.length <= tamanhoPagina) {
    paginacao.hidden = true;
    return;
  }
  let paginaAtual = 1;
  const renderizar = () => {
    const totalPaginas = Math.ceil(linhas.length / tamanhoPagina);
    const inicio = (paginaAtual - 1) * tamanhoPagina;
    linhas.forEach((linha, indice) => {
      linha.hidden = indice < inicio || indice >= inicio + tamanhoPagina;
    });
    paginacao.replaceChildren();
    for (let pagina = 1; pagina <= totalPaginas; pagina += 1) {
      const botao = document.createElement("button");
      botao.type = "button";
      botao.textContent = String(pagina);
      botao.className = pagina === paginaAtual ? "pagina-atual" : "";
      botao.addEventListener("click", () => { paginaAtual = pagina; renderizar(); });
      paginacao.appendChild(botao);
    }
  };
  renderizar();
})();
