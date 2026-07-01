// Aviso offline + interceptação de submit da tela BSR/ERB Fake
(function () {
  const aviso = document.getElementById("offline-aviso-bsr");

  function estaOffline() {
    return window.APP_OFFLINE === true || !navigator.onLine;
  }

  function atualizarAviso() {
    if (aviso) aviso.style.display = estaOffline() ? "block" : "none";
  }

  window.addEventListener("app-connectivity", atualizarAviso);
  window.addEventListener("online", atualizarAviso);
  window.addEventListener("offline", atualizarAviso);
  atualizarAviso();

  const form = document.getElementById("form-bsr-erb");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    if (!estaOffline()) return; // online: deixa o POST normal acontecer
    e.preventDefault();

    const fd = new FormData(this);
    const dados = {
      tipo: fd.get("tipo") || "BSR/Jammer",
      regiao: fd.get("regiao") || "",
      lat: fd.get("lat") || "",
      lon: fd.get("lon") || "",
    };

    if (!dados.regiao) {
      alert("O campo 'Local' é obrigatório.");
      return;
    }

    try {
      await AppOffline.enfileirar("fila_bsr_erb", dados);
      const div = document.createElement("div");
      div.className = "flash flash-success";
      div.textContent = "📥 Salvo localmente. Será enviado ao reconectar.";
      this.parentElement.insertBefore(div, this);
      this.reset();
    } catch (err) {
      alert("Erro ao salvar localmente: " + err);
    }
  });
})();
