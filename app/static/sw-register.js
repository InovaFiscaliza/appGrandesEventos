// Registro do Service Worker (com auto-atualização)
(function () {
  if (!("serviceWorker" in navigator)) return;

  let recarregando = false;
  // Quando um novo SW assume o controle, recarrega a página uma vez
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (recarregando) return;
    recarregando = true;
    window.location.reload();
  });

  navigator.serviceWorker
    .register("/sw.js?v=84")
    .then((reg) => {
      console.log("SW registrado:", reg.scope);
      // Verifica atualização a cada carregamento
      reg.update();
      // Se houver um SW novo esperando, ativa imediatamente
      if (reg.waiting) reg.waiting.postMessage({ type: "SKIP_WAITING" });
      reg.addEventListener("updatefound", () => {
        const novo = reg.installing;
        if (!novo) return;
        novo.addEventListener("statechange", () => {
          if (novo.state === "installed" && navigator.serviceWorker.controller) {
            novo.postMessage({ type: "SKIP_WAITING" });
          }
        });
      });
    })
    .catch((e) => console.error("SW falhou:", e));
})();
