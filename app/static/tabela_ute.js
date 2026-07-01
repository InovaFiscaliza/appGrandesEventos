// Copiar texto de células ao clicar (delegação de evento)
(function () {
  function copiar(el) {
    const text = el.textContent.trim();
    function feedback() {
      const orig = el.textContent;
      el.textContent = "Copiado!";
      setTimeout(() => {
        el.textContent = orig;
      }, 1500);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(feedback, fallback);
    } else {
      fallback();
    }
    function fallback() {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      feedback();
    }
  }

  document.addEventListener("click", function (e) {
    const cell = e.target.closest(".copyable-cell");
    if (cell) copiar(cell);
  });
})();
