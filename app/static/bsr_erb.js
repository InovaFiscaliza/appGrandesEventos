// Aviso offline + interceptação de submit da tela BSR/ERB Fake
(function () {
  const aviso = document.getElementById("offline-aviso-bsr");
  if (aviso) aviso.style.display = "none";

  const form = document.getElementById("form-bsr-erb");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    if (form.dataset.enviando === "1") return;
    form.dataset.enviando = "1";
    const botao = form.querySelector('button[type="submit"]');
    if (botao) botao.disabled = true;

    // Tenta enviar online primeiro
    const fd = new FormData(this);
    const destino = this.getAttribute("action") || "/bsr-erb";
    try {
      const resp = await fetch(destino, {
        method: "POST",
        body: fd,
      });
      if (resp.ok) {
        if (resp.redirected) {
          window.location.href = resp.url;
        } else {
          const html = await resp.text();
          document.open();
          document.write(html);
          document.close();
        }
        return;
      }
      // Se o servidor recusou, cai no offline
    } catch (_e) {
      // Falha de rede — continua para salvar offline
    }

    if (destino !== "/bsr-erb") {
      delete form.dataset.enviando;
      if (botao) botao.disabled = false;
      alert("Não é possível editar este registro sem conexão.");
      return;
    }

    const possuiFotos = fd.getAll("imagens").some((arquivo) => arquivo instanceof File && arquivo.size > 0);
    if (possuiFotos) {
      delete form.dataset.enviando;
      if (botao) botao.disabled = false;
      alert("As fotos precisam de conexão para serem enviadas. Mantenha o formulário aberto e tente novamente quando a conexão voltar.");
      return;
    }
    const dados = {
      tipo: fd.get("tipo") || "BSR/Jammer",
      regiao: fd.get("regiao") || "",
      lat: fd.get("lat") || "",
      lon: fd.get("lon") || "",
      observacoes: fd.get("observacoes") || "",
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
      delete form.dataset.enviando;
      if (botao) botao.disabled = false;
    } catch (err) {
      delete form.dataset.enviando;
      if (botao) botao.disabled = false;
      alert("Erro ao salvar localmente: " + err);
    }
  });
})();
