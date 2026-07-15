const STORE = "cache_pendencias";
let pendencias = [];

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
  setSelect("f-autz", row.autorizado || "Não licenciável");
  setSelect("f-interf", row.interferente || "Indefinido");
  setSelect("f-situ", row.situacao || "Pendente");
  document.getElementById("bloco-form").style.display = "block";
}

function popularSelect(lista) {
  const sel = document.getElementById("sel-pendencia");
  sel.innerHTML = '<option value="">Escolha uma pendência...</option>';
  lista.forEach((row) => {
    const opt = document.createElement("option");
    opt.value = row.row_key;
    opt.textContent = row.label;
    sel.appendChild(opt);
  });
  document.getElementById("bloco-select").style.display = lista.length
    ? "block"
    : "none";
  document.getElementById("msg-vazio").style.display = lista.length
    ? "none"
    : "block";
}

document
  .getElementById("sel-pendencia")
  .addEventListener("change", function () {
    const row = pendencias.find((r) => r.row_key === this.value);
    if (row) preencherForm(row);
    else document.getElementById("bloco-form").style.display = "none";
  });

async function carregarPendencias() {
  try {
    const resp = await fetch("/api/pendencias");
    if (resp.status === 401) {
      window.location.href = "/";
      return;
    }
    const dados = await resp.json();
    pendencias = dados;
    await AppOffline.salvarTodos(STORE, dados);
    document.getElementById("offline-aviso").style.display = "none";
  } catch (e) {
    console.warn("Falha ao buscar online, usando cache:", e);
    pendencias = await AppOffline.lerTodos(STORE);
    document.getElementById("offline-aviso").style.display = "block";
  }
  popularSelect(pendencias);
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
    // Offline real (placa desligada): enfileira direto, sem esperar timeout do servidor
    if (window.APP_OFFLINE === true || !navigator.onLine) {
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
          document.getElementById("sel-pendencia").value = "";
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
