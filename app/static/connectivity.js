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
    aplicarEstado(!navigator.onLine);
  }

  window.addEventListener("online", checarConexao);
  window.addEventListener("offline", checarConexao);
  checarConexao();
})();
