// Aviso offline + interceptação de submit da tela BSR/ERB Fake
(function () {
  const aviso = document.getElementById("offline-aviso-bsr");
  if (aviso) aviso.style.display = "none";

  const form = document.getElementById("form-bsr-erb");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    // Tenta enviar online primeiro
    const fd = new FormData(this);
    try {
      const resp = await fetch("/bsr_erb/salvar", {
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

    e.preventDefault();
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
