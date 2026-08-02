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
document.getElementById("freq").addEventListener("change", async function () {
  const val = parseFloat(this.value);
  const warn = document.getElementById("freq-warning");
  const online = !(window.APP_OFFLINE === true) && navigator.onLine;
  if (val > 0 && online) {
    try {
      const resp = await fetch("/check-freq?freq=" + val);
      const data = await resp.json();
      if (data.conflito) {
        warn.textContent =
          "⚠️ AVISO (apenas): Essa frequência consta na Planilha - Aba: " +
          data.conflito;
        warn.style.display = "block";
      } else {
        warn.style.display = "none";
      }
    } catch (e) {
      warn.style.display = "none";
    }
  } else {
    warn.style.display = "none";
  }
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
    "Autorizado? (Q)": "",
    "UTE?": fd.get("ute") ? "1" : "",
    "Processo SEI ou Ato UTE": fd.get("proc") || "",
    "Observações/Detalhes/Contatos": fd.get("obs") || "",
    "Responsável pela emissão": "",
    "Interferente?": fd.get("interferente") || "",
    "Situação": fd.get("situacao") || "Pendente",
  })
);
