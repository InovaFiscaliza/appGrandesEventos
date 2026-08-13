window.abrirZoomImagem = function (src, alt) {
  let modal = document.getElementById("imagem-zoom-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "imagem-zoom-modal";
    modal.className = "imagem-zoom-modal";
    modal.innerHTML = `
      <button type="button" class="imagem-zoom-fechar" aria-label="Fechar imagem">×</button>
      <img class="imagem-zoom-conteudo" alt="">
    `;
    document.body.appendChild(modal);
    modal.querySelector(".imagem-zoom-fechar").addEventListener("click", () => {
      modal.classList.remove("aberto");
    });
    modal.addEventListener("click", (evento) => {
      if (evento.target === modal) modal.classList.remove("aberto");
    });
  }
  const imagem = modal.querySelector(".imagem-zoom-conteudo");
  imagem.src = src;
  imagem.alt = alt || "Imagem ampliada";
  modal.classList.add("aberto");
};

document.addEventListener("keydown", (evento) => {
  if (evento.key === "Escape") {
    document.getElementById("imagem-zoom-modal")?.classList.remove("aberto");
  }
});

(() => {
  function configurarUpload(inputId, listaId) {
    const input = document.getElementById(inputId);
    const lista = document.getElementById(listaId);
    if (!input || !lista) return;

    input.addEventListener("change", () => {
      lista.replaceChildren();
      Array.from(input.files).forEach((arquivo) => {
        const item = document.createElement("li");
        item.className = "imagem-preview-item";
        const preview = document.createElement("img");
        preview.src = URL.createObjectURL(arquivo);
        preview.alt = arquivo.name;
        preview.title = arquivo.name;
        preview.addEventListener("click", () => {
          window.abrirZoomImagem(preview.src, arquivo.name);
        });
        item.appendChild(preview);
        lista.appendChild(item);
      });
    });
  }

  configurarUpload("imagens-inserir", "lista-imagens-inserir");
  configurarUpload("imagens-bsr-erb", "lista-imagens-bsr-erb");
  configurarUpload("imagens-edicao", "lista-imagens-edicao");
  configurarUpload("imagens-teste", "lista-imagens-teste");
})();