(() => {
  const popup = document.getElementById("fiscais-popup");
  const abrir = document.getElementById("abrir-fiscais");
  const fechar = document.getElementById("fechar-fiscais");
  const formulario = document.getElementById("form-fiscal");
  const corpo = document.getElementById("fiscais-tbody");
  const mensagem = document.getElementById("fiscal-mensagem");
  if (!popup || !abrir || !fechar || !formulario || !corpo) return;

  const atualizarCoordenadores = () => {
    const lista = document.getElementById("coordenadores-evento");
    if (!lista) return;
    const selecionados = new Set(
      Array.from(lista.querySelectorAll('input[name="coordenador_responsavel"]:checked'))
        .map((checkbox) => checkbox.value)
    );
    lista.replaceChildren();
    document.querySelectorAll('#fiscais-evento input[name="fiscais_evento"]:checked')
      .forEach((checkbox) => {
        if (checkbox.dataset.fiscalFuncao !== "Coordenação") return;
        const fiscalId = checkbox.value;
        const nome = checkbox.dataset.fiscalNome || "";
        const texto = checkbox.closest("label")?.querySelector("span:last-child")?.textContent || nome;
        const label = document.createElement("label");
        label.className = "unidade-checkbox";
        label.innerHTML = `
          <input type="checkbox" name="coordenador_responsavel" value="${fiscalId}">
          <span class="unidade-checkbox-mark" aria-hidden="true"></span>
          <span></span>
        `;
        label.querySelector("input").checked = selecionados.has(fiscalId);
        label.querySelector("span:last-child").textContent = texto;
        lista.appendChild(label);
      });
    if (!lista.querySelector('input[name="coordenador_responsavel"]')) {
      const vazio = document.createElement("span");
      vazio.className = "fiscais-vazio";
      vazio.textContent = "Nenhum fiscal de Coordenação participante.";
      lista.appendChild(vazio);
    }
  };

  document.getElementById("fiscais-evento")?.addEventListener("change", atualizarCoordenadores);
  atualizarCoordenadores();

  const fecharPopup = () => {
    popup.hidden = true;
    document.body.classList.remove("fiscais-popup-aberto");
  };

  abrir.addEventListener("click", () => {
    popup.hidden = false;
    document.body.classList.add("fiscais-popup-aberto");
    document.getElementById("fiscal-nome")?.focus();
  });
  fechar.addEventListener("click", fecharPopup);
  popup.addEventListener("click", (evento) => {
    if (evento.target === popup) fecharPopup();
  });
  document.addEventListener("keydown", (evento) => {
    if (evento.key === "Escape" && !popup.hidden) fecharPopup();
  });

  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mensagem.textContent = "";
    const resposta = await fetch("/fiscais", {
      method: "POST",
      body: new FormData(formulario),
      headers: { Accept: "application/json" },
    });
    const dados = await resposta.json();
    if (!resposta.ok || !dados.ok) {
      mensagem.className = "fiscal-mensagem erro";
      mensagem.textContent = dados.mensagem || "Não foi possível cadastrar o fiscal.";
      return;
    }
    document.getElementById("fiscais-vazio")?.remove();
    const fiscal = dados.fiscal;
    const linha = document.createElement("tr");
    linha.dataset.fiscalId = fiscal.id;
    linha.innerHTML = `<td></td><td></td><td></td><td><form class="fiscal-exclusao-form" method="post" action="/fiscais/${fiscal.id}/excluir"><button type="submit" class="btn fiscal-excluir">Excluir</button></form></td>`;
    linha.children[0].textContent = fiscal.nome;
    linha.children[1].textContent = `${fiscal.local_anatel} - ${fiscal.local_anatel_nome}`;
    linha.children[2].textContent = fiscal.funcao_evento;
    corpo.appendChild(linha);
    const listaEvento = document.getElementById("fiscais-evento");
    document.getElementById("fiscais-vazio")?.remove();
    if (listaEvento) {
      const participante = document.createElement("label");
      participante.className = "unidade-checkbox";
      participante.innerHTML = `
        <input type="checkbox" name="fiscais_evento" value="${fiscal.id}" data-fiscal-nome="${fiscal.nome}" data-fiscal-funcao="${fiscal.funcao_evento}">
        <span class="unidade-checkbox-mark" aria-hidden="true"></span>
        <span></span>
      `;
      participante.querySelector("span:last-child").textContent =
        `${fiscal.nome} - ${fiscal.local_anatel} - ${fiscal.funcao_evento}`;
      listaEvento.appendChild(participante);
      participante.querySelector('input[name="fiscais_evento"]')?.addEventListener("change", atualizarCoordenadores);
      atualizarCoordenadores();
    }
    formulario.reset();
    mensagem.className = "fiscal-mensagem sucesso";
    mensagem.textContent = "Fiscal cadastrado com sucesso.";
  });

  corpo.addEventListener("submit", async (evento) => {
    const formularioExclusao = evento.target.closest(".fiscal-exclusao-form");
    if (!formularioExclusao) return;
    evento.preventDefault();
    const resposta = await fetch(formularioExclusao.action, { method: "POST", headers: { Accept: "application/json" } });
    if (!resposta.ok) return;
    const linha = formularioExclusao.closest("tr");
    const fiscalId = linha.dataset.fiscalId;
    document.querySelector(`#fiscais-evento input[value="${fiscalId}"]`)?.closest("label")?.remove();
    linha.remove();
    atualizarCoordenadores();
    if (!corpo.querySelector("tr")) {
      corpo.innerHTML = '<tr id="fiscais-vazio"><td colspan="4">Nenhum fiscal cadastrado.</td></tr>';
    }
  });
})();