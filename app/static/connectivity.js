// Detecção ATIVA de conectividade.
// navigator.onLine não é confiável (adaptadores virtuais mantêm 'true'
// mesmo com a placa de rede física desligada). Por isso testamos a
// conectividade real com um recurso externo periodicamente.
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
    }, 4000);
    fetch("https://www.gstatic.com/generate_204", {
      mode: "no-cors",
      cache: "no-store",
      signal: ctrl.signal,
    })
      .then(function () {
        clearTimeout(t);
        aplicarEstado(false);
      })
      .catch(function () {
        clearTimeout(t);
        aplicarEstado(true);
      });
  }

  window.addEventListener("online", checarConexao);
  window.addEventListener("offline", checarConexao);
  setInterval(checarConexao, 5000);
  checarConexao();
})();
