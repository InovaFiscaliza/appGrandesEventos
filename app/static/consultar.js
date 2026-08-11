const STORE = "cache_pendencias";
let pendencias = [];
let paginaAtual = 1;
const ITENS_POR_PAGINA = 10;

function setSelect(id, val) {
  const el = document.getElementById(id);
  if (!el) return;
  for (const opt of el.options) {
    if (opt.value === val) {
      opt.selected = true;
      return;
    }
  }
}

function preencherForm(row) {
  document.getElementById("f-row_key").value = row.row_key || "";
  document.getElementById("f-fonte").value = row.fonte || "";
  document.getElementById("f-id_val").value = row.id || "";
  document.getElementById("f-estacao_raw").value = row.estacao_raw || "";
  document.getElementById("f-id").value = row.id || "";
  document.getElementById("f-local").value = row.local || "";
  document.getElementById("f-fiscal").value = row.fiscal || "";
  document.getElementById("f-data").value = row.data || "";
  document.getElementById("f-hora").value = row.hora || "";
  document.getElementById("f-freq").value = row.freq || "";
  document.getElementById("f-largura").value = row.largura || "";
  document.getElementById("f-faixa").value = row.faixa || "";
  document.getElementById("f-proc").value = row.processo_sei || "";
  document.getElementById("f-obs").value = row.ocorrencia || "";
  document.getElementById("f-cient").value = row.ciente || "";
  document.getElementById("f-ute").checked = ["sim", "true", "1", "ok"].includes(
    (row.ute || "").toLowerCase()
  );
  setSelect("f-ident", row.identificacao || "");
  setSelect("f-autz", row.autorizado || "");
  setSelect("f-interf", row.interferente || "");
  setSelect("f-situ", row.situacao || "");
  document.getElementById("f-imagens-excluir").value = "";
  carregarImagensOcorrencia(row.id);
  document.getElementById("bloco-form").style.display = "block";
  document.getElementById("consultar-voltar").style.display = "none";
}

async function carregarImagensOcorrencia(id) {
  const lista = document.getElementById("lista-imagens-salvas");
  if (!lista) return;
  lista.replaceChildren();
  try {
    const resposta = await fetch(`/api/ocorrencia-imagens?id=${encodeURIComponent(id)}`);
    if (!resposta.ok) throw new Error(`Falha HTTP ${resposta.status}`);
    const imagens = await resposta.json();
    imagens.forEach((imagem) => {
      const item = document.createElement("li");
      item.className = "imagem-preview-item";
      const preview = document.createElement("img");
      preview.src = imagem.url;
      preview.alt = imagem.nome_arquivo;
      preview.title = imagem.nome_arquivo;
      preview.addEventListener("click", () => {
        if (window.abrirZoomImagem) {
          window.abrirZoomImagem(imagem.url, imagem.nome_arquivo);
        }
      });
      item.appendChild(preview);
      const excluir = document.createElement("button");
      excluir.type = "button";
      excluir.className = "imagem-preview-excluir";
      excluir.setAttribute("aria-label", `Excluir ${imagem.nome_arquivo}`);
      excluir.title = "Excluir imagem";
      excluir.textContent = "🗑️";
      excluir.addEventListener("click", () => {
        const campo = document.getElementById("f-imagens-excluir");
        const ids = campo.value ? campo.value.split(",") : [];
        if (!ids.includes(String(imagem.id))) ids.push(String(imagem.id));
        campo.value = ids.filter(Boolean).join(",");
        item.remove();
      });
      item.appendChild(excluir);
      lista.appendChild(item);
    });
  } catch (erro) {
    console.warn("Não foi possível carregar as imagens da ocorrência:", erro);
  }
}

function textoSeguro(valor) {
  return String(valor || "");
}

function formatarInicio(row) {
  const data = textoSeguro(row.data);
  const hora = textoSeguro(row.hora);
  return [data, hora].filter(Boolean).join(" ");
}

function renderizarTabela(lista) {
  const tbody = document.getElementById("pendencias-tbody");
  const totalPaginas = Math.max(1, Math.ceil(lista.length / ITENS_POR_PAGINA));
  paginaAtual = Math.min(paginaAtual, totalPaginas);
  const inicio = (paginaAtual - 1) * ITENS_POR_PAGINA;
  const pagina = lista.slice(inicio, inicio + ITENS_POR_PAGINA);
  tbody.innerHTML = "";

  pagina.forEach((row) => {
    const tr = document.createElement("tr");
    tr.dataset.rowKey = row.row_key;
    const valores = [
      textoSeguro(row.id),
      textoSeguro(row.estacao_raw || row.fonte),
      textoSeguro(row.local),
      formatarInicio(row),
      textoSeguro(row.freq),
      textoSeguro(row.largura),
      textoSeguro(row.faixa),
      textoSeguro(row.situacao) || "Pendente",
    ];
    const acao = document.createElement("td");
    acao.className = "pendencia-action-col";
    const botao = document.createElement("button");
    botao.type = "button";
    botao.className = "pendencia-expandir";
    botao.setAttribute("aria-label", `Abrir emissão ${textoSeguro(row.id)}`);
    botao.textContent = "+";
    acao.appendChild(botao);
    tr.appendChild(acao);
    valores.forEach((valor, indice) => {
      const celula = document.createElement("td");
      celula.textContent = valor;
      if (indice === 0) celula.className = "pendencia-id";
      tr.appendChild(celula);
    });
    tr.addEventListener("click", () => selecionarPendencia(row));
    tbody.appendChild(tr);
  });
  renderizarPaginacao(lista.length, totalPaginas);
}

function renderizarPaginacao(totalItens, totalPaginas) {
  const paginacao = document.getElementById("paginacao-pendencias");
  paginacao.innerHTML = "";
  const adicionarBotao = (texto, pagina, disabled = false, atual = false) => {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.textContent = texto;
    botao.disabled = disabled;
    botao.className = atual ? "pagina-atual" : "";
    botao.addEventListener("click", () => {
      paginaAtual = pagina;
      renderizarTabela(pendencias);
    });
    paginacao.appendChild(botao);
  };
  adicionarBotao("«", 1, paginaAtual === 1);
  adicionarBotao("‹", Math.max(1, paginaAtual - 1), paginaAtual === 1);
  for (let pagina = 1; pagina <= totalPaginas; pagina += 1) {
    if (totalPaginas > 7 && pagina > 3 && pagina < totalPaginas - 2) {
      if (pagina === 4) {
        const separador = document.createElement("span");
        separador.textContent = "…";
        paginacao.appendChild(separador);
      }
      continue;
    }
    adicionarBotao(String(pagina), pagina, false, pagina === paginaAtual);
  }
  adicionarBotao("›", Math.min(totalPaginas, paginaAtual + 1), paginaAtual === totalPaginas);
  adicionarBotao("»", totalPaginas, paginaAtual === totalPaginas);
}

function selecionarPendencia(row) {
  document.querySelectorAll(".pendencias-table tbody tr").forEach((linha) => {
    linha.classList.toggle("pendencia-selecionada", linha.dataset.rowKey === row.row_key);
  });
  const progresso = document.getElementById("progresso-pendencias");
  if (progresso) {
    progresso.textContent = `${pendencias.length} pendência(s) aguardando tratamento.`;
  }
  preencherForm(row);
  const historico = document.getElementById("btn-consultar-historico");
  if (historico) {
    historico.href = `/consultar/historico?id=${encodeURIComponent(row.id || "")}`;
  }
  document.getElementById("bloco-form").scrollIntoView({ behavior: "smooth", block: "start" });
}

function popularTabela(lista) {
  const selectedKey = new URLSearchParams(window.location.search).get("key") || "";
  paginaAtual = 1;
  document.getElementById("bloco-select").style.display = lista.length ? "block" : "none";
  document.getElementById("msg-vazio").style.display = lista.length ? "none" : "block";
  document.getElementById("consultar-voltar").style.display = "block";
  if (!lista.length) return;
  document.getElementById("progresso-pendencias").textContent = `${lista.length} pendência(s) aguardando tratamento.`;
  renderizarTabela(lista);
  if (selectedKey) {
    const row = lista.find((item) => item.row_key === selectedKey);
    if (row) selecionarPendencia(row);
  }
}

async function carregarPendencias() {
  try {
    const resp = await fetch(`/api/pendencias?_=${Date.now()}`, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    if (resp.status === 401) {
      window.location.href = "/";
      return;
    }
    if (!resp.ok) throw new Error(`Falha HTTP ${resp.status}`);
    const dados = await resp.json();
    pendencias = dados;
    await AppOffline.salvarTodos(STORE, dados);
    document.getElementById("offline-aviso").style.display = "none";
  } catch (e) {
    console.warn("Falha ao buscar online, usando cache:", e);
    pendencias = await AppOffline.lerTodos(STORE);
    document.getElementById("offline-aviso").style.display = "block";
  }
  popularTabela(pendencias);
}

carregarPendencias();

// ─── Interceptação do submit de edição em modo offline ───────────
function extrairDadosEdicao() {
  const g = (id) => (document.getElementById(id) || {}).value || "";
  return {
    fonte: g("f-fonte"),
    id_val: g("f-id_val"),
    estacao_raw: g("f-estacao_raw"),
    row_key: g("f-row_key"),
    "Identificação": g("f-ident"),
    "Autorizado?": g("f-autz"),
    "UTE?": document.getElementById("f-ute").checked ? "Sim" : "Não",
    "Processo SEI UTE": g("f-proc"),
    "Ocorrência (observações)": g("f-obs"),
    "Alguém mais ciente?": g("f-cient"),
    "Interferente?": g("f-interf"),
    "Situação": g("f-situ"),
  };
}

document
  .getElementById("form-consultar")
  .addEventListener("submit", function (e) {
    const possuiImagens = document.getElementById("imagens-edicao")?.files?.length > 0;
    // Offline real (placa desligada): enfileira direto, sem esperar timeout do servidor
    // Arquivos não podem ser serializados na fila JSON; com anexos, deixe o
    // navegador enviar o multipart diretamente ao endpoint.
    if ((window.APP_OFFLINE === true || !navigator.onLine) && !possuiImagens) {
      e.preventDefault();
      const dados = extrairDadosEdicao();
      AppOffline.enfileirar("fila_edicoes", dados)
        .then(() => {
          const ref = document.querySelector(".info-green");
          AppOfflineUI.mostrarSucesso(
            ref,
            "📥 Alteração salva localmente. Será enviada ao reconectar."
          );
          document.getElementById("bloco-form").style.display = "none";
          document.getElementById("consultar-voltar").style.display = "block";
        })
        .catch((err) =>
          AppOfflineUI.mostrarErro("Erro ao salvar localmente: " + err)
        );
    }
    // Online: deixa o POST normal seguir (servidor tem fallback offline_salvo)
  });

// ─── Fallback offline do servidor (edição salva localmente) ──────
(function () {
  const el = document.getElementById("offline-edicao-data");
  if (!el) return;
  let dados;
  try {
    dados = JSON.parse(el.textContent);
  } catch (e) {
    console.error("Dados offline inválidos:", e);
    return;
  }
  function salvarEdicaoOffline() {
    AppOffline.enfileirar("fila_edicoes", dados)
      .then(() => {
        const ref =
          document.querySelector(".info-green") ||
          document.querySelector(".container").firstChild;
        AppOfflineUI.mostrarSucesso(
          ref,
          "📥 Alteração salva localmente. Será enviada ao reconectar."
        );
      })
      .catch((err) => console.error("Erro ao salvar edição offline:", err));
  }
  if (typeof AppOffline !== "undefined") {
    salvarEdicaoOffline();
  } else {
    document.addEventListener("DOMContentLoaded", salvarEdicaoOffline);
  }
})();
