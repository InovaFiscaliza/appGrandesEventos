// Detecção ATIVA de conectividade.
// Usa o próprio servidor da aplicação como referência (/api/ping)
// em vez de serviço externo, evitando falsos positivos com proxy corporativo.
(function () {
  window.APP_OFFLINE = !navigator.onLine;

  function aplicarEstado(offline) {
    var mudou = window.APP_OFFLINE !== offline;
    window.APP_OFFLINE = offline;
    var banner = document.getElementById("offline-banner");
    if (banner) banner.classList.toggle("show", offline);
    if (mudou) {
      // Notifica o resto do app (ex.: sincronizar ao voltar online)
      window.dispatchEvent(
        new CustomEvent("app-connectivity", { detail: { offline: offline } })
      );
    }
  }

  function checarConexao() {
    if (!navigator.onLine) {
      aplicarEstado(true);
      return;
    }
    var ctrl = new AbortController();
    var t = setTimeout(function () {
      ctrl.abort();
    }, 6000);
    // Usa endpoint local em vez de serviço externo
    fetch("/api/ping", {
      cache: "no-store",
      signal: ctrl.signal,
    })
      .then(function (r) {
        clearTimeout(t);
        aplicarEstado(!r.ok);
      })
      .catch(function () {
        clearTimeout(t);
        aplicarEstado(true);
      });
  }

  window.addEventListener("online", checarConexao);
  window.addEventListener("offline", checarConexao);
  setInterval(checarConexao, 8000);
  checarConexao();
})();
