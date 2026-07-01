// Auto-submit ao selecionar um evento
(function () {
  const sel = document.querySelector('select[name="evento_key"]');
  if (sel) {
    sel.addEventListener("change", function () {
      if (this.form) this.form.submit();
    });
  }
})();
