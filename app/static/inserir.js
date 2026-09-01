// ─── Aviso offline local ─────────────────────────────────────
(function () {
  const avisoEl = document.getElementById("offline-aviso-inserir");
  if (avisoEl) {
    // O aviso só aparece se o fetch ao servidor falhar (tratado no carregamento)
    avisoEl.style.display = "none";
  }
})();

// ─── Fallback offline do servidor ────────────────────────────
(function () {
  const el = document.getElementById("offline-inserir-data");
  if (!el) return;
  const store = el.dataset.store || "fila_envio";
  let dados;
  try {
    dados = JSON.parse(el.textContent);
  } catch (e) {
    console.error("Dados offline inválidos:", e);
    return;
  }
  function salvarOffline() {
    AppOffline.enfileirar(store, dados)
      .then(() => {
        AppOfflineUI.mostrarSucesso(
          document.getElementById("form-inserir"),
          "📥 Salvo localmente. Será enviado ao reconectar."
        );
      })
      .catch((err) => console.error("Erro ao salvar offline:", err));
  }
  // Aguarda AppOffline ficar disponível (pode estar carregando via cache)
  if (typeof AppOffline !== "undefined") {
    salvarOffline();
  } else {
    document.addEventListener("DOMContentLoaded", salvarOffline);
  }
})();

// ─── Check frequência (online apenas) ────────────────────────
(() => {
  const adicionar = document.getElementById("adicionar-fiscal-participante");
  const seletorArea = document.getElementById("seletor-fiscal-participante");
  const seletor = document.getElementById("fiscal-participante");
  const lista = document.getElementById("lista-fiscais-participantes");
  if (!adicionar || !seletorArea || !seletor || !lista) return;

  adicionar.addEventListener("click", () => {
    seletorArea.hidden = false;
    seletor.focus();
  });
  seletor.addEventListener("change", () => {
    const opcao = seletor.selectedOptions[0];
    if (!opcao?.value || lista.querySelector(`[data-fiscal-id="${opcao.value}"]`)) return;
    const item = document.createElement("span");
    item.dataset.fiscalId = opcao.value;
    item.append(document.createTextNode(`${opcao.textContent} `));
    const remover = document.createElement("button");
    remover.type = "button";
    remover.className = "fiscal-participante-remover";
    remover.textContent = "×";
    remover.title = "Remover fiscal";
    remover.setAttribute("data-sem-confirmacao", "");
    remover.setAttribute("aria-label", `Remover ${opcao.textContent}`);
    remover.addEventListener("click", () => item.remove());
    const campo = document.createElement("input");
    campo.type = "hidden";
    campo.name = "fiscais_participantes";
    campo.value = opcao.value;
    item.append(remover, campo);
    lista.appendChild(item);
    seletor.value = "";
    seletorArea.hidden = true;
  });
  lista.querySelectorAll("button").forEach((botao) => {
    botao.addEventListener("click", () => botao.closest("span")?.remove());
  });
})();

async function consultarConflitoFrequencia() {
  const val = parseFloat(document.getElementById("freq")?.value || "0");
  const largura = parseFloat(document.getElementById("larg")?.value || "0");
  const local = document.getElementById("local")?.value || "";
  const warn = document.getElementById("freq-warning");
  const online = !(window.APP_OFFLINE === true) && navigator.onLine;
  if (!warn) return;
  if (!(val > 0) || !online) {
    warn.style.display = "none";
    return;
  }
  try {
    const parametros = new URLSearchParams({ freq: val, larg: largura, local });
    const resp = await fetch("/check-freq?" + parametros);
    const data = await resp.json();
    if (data.conflito) {
      warn.textContent =
        "⚠️ AVISO: existe equipamento usando essa frequência: " + data.conflito;
      warn.style.display = "block";
    } else {
      warn.style.display = "none";
    }
  } catch (e) {
    warn.style.display = "none";
  }
}

["freq", "larg", "local"].forEach((id) => {
  document.getElementById(id)?.addEventListener("change", consultarConflitoFrequencia);
});

// ─── Interceptação de submit offline ─────────────────────────
AppOffline.interceptarSubmit(
  document.getElementById("form-inserir"),
  "/inserir",
  "fila_envio",
  (fd) => ({
    "Dia": fd.get("dia") || "",
    "Hora": fd.get("hora") || "",
    "Fiscal": fd.get("fiscal") || "",
    "Local/Região": fd.get("local") || "",
    "Frequência em MHz": fd.get("freq") || "",
    "Largura em kHz": fd.get("larg") || "",
    "Faixa de Frequência": fd.get("faixa") || "",
    "Identificação": fd.get("ident") || "",
    "Estação ID": fd.get("estacao_id") || "",
    "Fiscais participantes": fd.getAll("fiscais_participantes"),
    "Autorizado? (Q)": "",
    "UTE?": fd.get("ute") ? "1" : "",
    "Processo SEI ou Ato UTE": fd.get("proc") || "",
    "Observações/Detalhes/Contatos": fd.get("obs") || "",
    "Responsável pela emissão": "",
    "Interferente?": fd.get("interferente") || "",
    "Situação": fd.get("situacao") || "Pendente",
  }),
  {
    beforeSubmit: async (fd) => {
      const valor = parseFloat(fd.get("freq"));
      const largura = parseFloat(fd.get("larg") || "0");
      const local = fd.get("local") || "";
      const warn = document.getElementById("freq-warning");
      if (!(valor > 0) || !navigator.onLine || window.APP_OFFLINE === true) {
        return true;
      }
      try {
        const parametros = new URLSearchParams({ freq: valor, larg: largura, local });
        const resp = await fetch("/check-freq?" + parametros);
        const data = await resp.json();
        if (!data.conflito) return true;
        warn.textContent =
          "⚠️ Aviso: existe equipamento usando essa frequência (" +
          data.conflito + ").";
        warn.style.display = "block";
        return true;
      } catch (e) {
        return true;
      }
    },
  }
);
