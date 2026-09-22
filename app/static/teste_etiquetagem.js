(() => {
  const imagensExcluir = document.querySelector('#imagens-teste-excluir');
  document.querySelectorAll('.imagem-preview-excluir[data-imagem-id]').forEach((botao) => {
    botao.setAttribute('data-confirmacao-imagem', 'true');
    botao.addEventListener('click', () => window.confirmarExclusaoImagem(() => {
      const campo = document.createElement('input');
      campo.type = 'hidden';
      campo.name = 'imagens_excluir';
      campo.value = botao.dataset.imagemId;
      imagensExcluir?.appendChild(campo);
      botao.closest('.imagem-preview-item')?.remove();
    }, botao));
  });

  const frequencia = document.querySelector('#frequencia');
  const passo = document.querySelector('#passo');
  const faixa = document.querySelector('#faixa');
  const lista = document.querySelector('#frequencias');
  const frequenciasEnviadas = document.querySelector('#frequencias-enviadas');
  const frequenciaConsulta = document.querySelector('#frequencia-consulta');
  const cpfCnpj = document.querySelector('#cpfcnpj');
  const cpfCnpjAjuda = document.querySelector('#cpfcnpj-ajuda');
  const etiqueta = document.querySelector('#numero-etiqueta');
  const etiquetaInicio = document.querySelector('#etiqueta-inicio');
  const etiquetaFinal = document.querySelector('#etiqueta-final');
  const numeroEquipamentos = document.querySelector('#numero-equipamentos');
  const perfis = [...document.querySelectorAll('input[name="perfil"]')];
  const permissaoRadios = [...document.querySelectorAll('input[name="permissao"]')];
  const grupoNumeroEtiqueta = document.querySelector('#grupo-numero-etiqueta');
  const form = document.querySelector('.teq-form');
  const adicionar = document.querySelector('#adicionar-frequencia');
  const remover = document.querySelector('#remover-frequencia');
  const popupFrequencia = document.querySelector('#popup-frequencia');
  const confirmarAdicionar = document.querySelector('#confirmar-adicionar-frequencia');
  const fecharPopupFrequencia = document.querySelector('#fechar-popup-frequencia');

  if (!frequencia || !passo || !faixa || !lista || !frequenciasEnviadas || !frequenciaConsulta || !cpfCnpj || !cpfCnpjAjuda || !etiqueta || !etiquetaInicio || !etiquetaFinal || !numeroEquipamentos || !form || !adicionar || !remover || !popupFrequencia || !confirmarAdicionar || !fecharPopupFrequencia) return;

  function abrirPopupFrequencia() {
    frequencia.value = '';
    passo.value = '';
    faixa.value = '';
    frequenciaConsulta.replaceChildren();
    frequenciaConsulta.classList.remove('teq-frequency-check-warning');
    frequencia.classList.remove('teq-invalid');
    popupFrequencia.hidden = false;
    frequencia.focus();
  }

  function fecharPopupFrequenciaFn() {
    popupFrequencia.hidden = true;
  }

  const invalidosServidor = new Set(
    JSON.parse(form.dataset.invalidFields || '[]')
  );

  function atualizarEstadoVisualCampo(elemento, erro) {
    if (!elemento) return;
    elemento.classList.toggle('teq-invalid', erro);
    if (!erro) elemento.classList.remove('teq-valid');
    const label = document.querySelector(`label[for="${elemento.id}"]`);
    if (label) {
      label.classList.toggle('teq-label-invalid', erro);
    }
  }

  function limparErroSePreenchido(campo, condicaoValida) {
    if (!invalidosServidor.has(campo)) return;
    atualizarEstadoVisualCampo(
      {
        entidade: document.querySelector('#entidade'),
        local: document.querySelector('#local'),
        frequencia_mhz: frequencia,
        passo,
        faixa,
        frequencias_selecionadas: lista,
        tipo_equipamento: document.querySelector('#tipo-equipamento'),
        numero_equipamentos: document.querySelector('#numero-equipamentos'),
        numero_etiqueta: etiquetaInicio,
      }[campo],
      !condicaoValida
    );
  }

  function formatarFrequencia(valor) {
    const numero = Number(String(valor ?? '').trim().replace(',', '.'));
    if (!Number.isFinite(numero) || numero <= 0) return null;
    return numero.toFixed(3).replace('.', ',');
  }

  function atualizarEstadoRemover() {
    remover.disabled = lista.selectedOptions.length === 0;
  }

  function manterUmaSelecao() {
    const selecionadas = [...lista.selectedOptions];
    if (selecionadas.length > 1) {
      selecionadas.slice(0, -1).forEach((opcao) => {
        opcao.selected = false;
      });
    }
    atualizarEstadoRemover();
  }

  function atualizarFrequenciasEnviadas() {
    frequenciasEnviadas.replaceChildren(
      ...[...lista.options].map((opcao) => {
        const campo = document.createElement('input');
        campo.type = 'hidden';
        campo.name = 'frequencias_selecionadas';
        campo.value = opcao.value;
        return campo;
      })
    );
  }

  function frequenciaJaNaLista(valor) {
    const numero = Number(String(valor ?? '').trim().replace(',', '.'));
    if (!Number.isFinite(numero) || numero <= 0) return false;
    return [...lista.options].some((opcao) => {
      const encontrada = opcao.value.match(/^\s*([\d.,]+)\s+MHz\b/);
      return encontrada
        && Number(encontrada[1].replace(',', '.')).toFixed(3) === numero.toFixed(3);
    });
  }

  function exibirConsulta(data, mensagemLocal = '') {
    const linhas = [];
    if (mensagemLocal) linhas.push(mensagemLocal);
    data.equipamentos.forEach((equipamento) => {
      linhas.push(`Equipamento com essa frequência já cadastrado: ${equipamento.entidade || 'Nome não informado'} | CPF/CNPJ: ${equipamento.cpf_cnpj || 'não informado'} | Tipo: ${equipamento.tipo_equipamento || 'não informado'} | Etiqueta: ${equipamento.numero_etiqueta || 'não informada'} | Local: ${equipamento.local || 'não informado'}`);
    });
    data.referencias.forEach((referencia) => {
      linhas.push(`Referência no banco: ${referencia.origem} | ${referencia.detalhe}`);
    });
    frequenciaConsulta.replaceChildren(
      ...linhas.flatMap((linha, indice) => {
        const texto = document.createTextNode(linha);
        return indice === 0 ? [texto] : [document.createElement('br'), texto];
      })
    );
    const conflito = linhas.length > 0;
    frequenciaConsulta.classList.toggle('teq-frequency-check-warning', conflito);
    frequencia.classList.toggle('teq-invalid', conflito);
  }

  async function consultarFrequencia(valor) {
    const numero = Number(String(valor ?? '').trim().replace(',', '.'));
    const mensagemLocal = frequenciaJaNaLista(numero) ? 'Esta frequência já está na lista.' : '';
    if (!Number.isFinite(numero) || numero <= 0) {
      frequenciaConsulta.replaceChildren();
      frequenciaConsulta.classList.remove('teq-frequency-check-warning');
      frequencia.classList.remove('teq-invalid');
      return null;
    }
    try {
      const registro = form.querySelector('input[name="registro_id"]')?.value;
      const larguraTexto = document.getElementById('passo')?.value || '';
      const largura = Number(larguraTexto.replace(/\./g, '').replace(',', '.').replace(/\s*kHz/i, '')) || 0;
      const parametros = new URLSearchParams({ frequencia: String(numero), largura_khz: largura });
      if (registro) parametros.set('excluir_id', registro);
      const resposta = await fetch(`/api/teste-etiquetagem/verificar-frequencia?${parametros}`);
      if (!resposta.ok) return null;
      const data = await resposta.json();
      exibirConsulta(data, mensagemLocal);
      return data;
    } catch (erro) {
      exibirConsulta({ equipamentos: [], referencias: [] }, mensagemLocal);
      return null;
    }
  }

  function validarCpfCnpj(valor) {
    const numeros = valor.replace(/\D/g, '');
    if (![11, 14].includes(numeros.length) || /^([0-9])\1+$/.test(numeros)) return false;

    if (numeros.length === 11) {
      let soma = 0;
      for (let indice = 0; indice < 9; indice += 1) {
        soma += Number(numeros[indice]) * (10 - indice);
      }
      let digito = (soma * 10 % 11) % 10;
      if (digito !== Number(numeros[9])) return false;
      soma = 0;
      for (let indice = 0; indice < 10; indice += 1) {
        soma += Number(numeros[indice]) * (11 - indice);
      }
      digito = (soma * 10 % 11) % 10;
      return digito === Number(numeros[10]);
    }

    const calcularDigito = (quantidade) => {
      const pesos = quantidade === 12
        ? [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        : [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
      const soma = pesos.reduce(
        (total, peso, indice) => total + Number(numeros[indice]) * peso,
        0
      );
      return soma % 11 < 2 ? 0 : 11 - soma % 11;
    };
    return calcularDigito(12) === Number(numeros[12])
      && calcularDigito(13) === Number(numeros[13]);
  }

  function atualizarValidacaoCpfCnpj() {
    const valor = cpfCnpj.value.trim();
    const numeros = valor.replace(/\D/g, '');
    cpfCnpj.classList.remove('teq-valid', 'teq-invalid');
    cpfCnpjAjuda.classList.remove('teq-valid', 'teq-invalid');

    if (!valor) {
      cpfCnpj.setCustomValidity('');
      cpfCnpjAjuda.textContent = 'Informe um CPF ou CNPJ válido, se necessário.';
      cpfCnpjAjuda.classList.remove('teq-valid', 'teq-invalid');
      if (invalidosServidor.has('cpf_cnpj')) {
        atualizarEstadoVisualCampo(cpfCnpj, false);
      }
      return;
    }
    if (![11, 14].includes(numeros.length)) {
      cpfCnpj.setCustomValidity('Digite um CPF com 11 ou um CNPJ com 14 números.');
      cpfCnpj.classList.add('teq-invalid');
      cpfCnpjAjuda.classList.add('teq-invalid');
      cpfCnpjAjuda.textContent = 'Digite um CPF com 11 ou um CNPJ com 14 números.';
      if (invalidosServidor.has('cpf_cnpj')) {
        atualizarEstadoVisualCampo(cpfCnpj, true);
      }
      return;
    }
    if (!validarCpfCnpj(valor)) {
      cpfCnpj.setCustomValidity('CPF/CNPJ inválido.');
      cpfCnpj.classList.add('teq-invalid');
      cpfCnpjAjuda.classList.add('teq-invalid');
      cpfCnpjAjuda.textContent = 'CPF/CNPJ inválido.';
      if (invalidosServidor.has('cpf_cnpj')) {
        atualizarEstadoVisualCampo(cpfCnpj, true);
      }
      return;
    }

    cpfCnpj.setCustomValidity('');
    cpfCnpj.classList.add('teq-valid');
    cpfCnpjAjuda.classList.add('teq-valid');
    cpfCnpjAjuda.textContent = numeros.length === 11 ? 'CPF válido.' : 'CNPJ válido.';
    if (invalidosServidor.has('cpf_cnpj')) {
      atualizarEstadoVisualCampo(cpfCnpj, false);
    }
  }

  function atualizarCpfParaPerfil() {
    const estrangeiro = perfis.find((radio) => radio.checked)?.value === 'estrangeiro';
    cpfCnpj.disabled = estrangeiro;
    cpfCnpj.setAttribute('aria-disabled', String(estrangeiro));
    if (estrangeiro) {
      cpfCnpj.value = '';
      cpfCnpj.setCustomValidity('');
      cpfCnpj.classList.remove('teq-valid', 'teq-invalid');
      cpfCnpjAjuda?.classList.remove('teq-valid', 'teq-invalid');
      if (cpfCnpjAjuda) cpfCnpjAjuda.textContent = 'CPF/CNPJ não se aplica a estrangeiro.';
    } else {
      if (cpfCnpjAjuda) cpfCnpjAjuda.textContent = 'Informe um CPF ou CNPJ válido, se necessário.';
      atualizarValidacaoCpfCnpj();
    }
  }

  cpfCnpj.addEventListener('input', atualizarValidacaoCpfCnpj);
  form.addEventListener('change', (event) => {
    if (event.target.matches('input[name="perfil"]')) {
      atualizarCpfParaPerfil();
    }
  });
  atualizarCpfParaPerfil();

  document.querySelector('#entidade')?.addEventListener('input', (event) => {
    limparErroSePreenchido('entidade', event.target.value.trim().length > 0);
  });
  document.querySelector('#local')?.addEventListener('input', (event) => {
    limparErroSePreenchido('local', event.target.value.trim().length > 0);
    const permissaoLocalTexto = document.querySelector('#permissao-local-texto');
    if (permissaoLocalTexto) permissaoLocalTexto.textContent = event.target.value;
  });
  frequencia.addEventListener('input', () => {
    const numero = Number(frequencia.value.trim().replace(',', '.'));
    limparErroSePreenchido('frequencia_mhz', Number.isFinite(numero) && numero > 0);
  });
  frequencia.addEventListener('change', () => consultarFrequencia(frequencia.value));
  passo.addEventListener('change', () => {
    limparErroSePreenchido('passo', passo.value.trim().length > 0);
  });
  faixa.addEventListener('change', () => {
    limparErroSePreenchido('faixa', faixa.value.trim().length > 0);
  });
  lista.addEventListener('change', () => {
    manterUmaSelecao();
    limparErroSePreenchido('frequencias_selecionadas', lista.options.length > 0);
  });
  document.querySelector('#tipo-equipamento')?.addEventListener('change', (event) => {
    limparErroSePreenchido('tipo_equipamento', event.target.value.trim().length > 0);
  });
  const DIGITOS_ETIQUETA = 5;

  function atualizarNumeroEtiqueta() {
    const inicioTexto = etiquetaInicio.value.trim();
    const inicio = Number(inicioTexto);
    const quantidade = Number(numeroEquipamentos.value);
    const valido = /^\d+$/.test(inicioTexto) && Number.isSafeInteger(inicio) && Number.isSafeInteger(quantidade) && quantidade >= 1;
    if (valido) {
      etiquetaFinal.value = String(inicio + quantidade - 1).padStart(DIGITOS_ETIQUETA, '0');
      etiqueta.value = inicioTexto.padStart(DIGITOS_ETIQUETA, '0');
    } else {
      etiquetaFinal.value = '';
      etiqueta.value = '';
    }
    limparErroSePreenchido('numero_etiqueta', etiqueta.value.length > 0);
  }

  [etiquetaInicio, numeroEquipamentos].forEach((campo) => {
    campo.addEventListener('input', atualizarNumeroEtiqueta);
  });
  numeroEquipamentos.addEventListener('change', atualizarNumeroEtiqueta);
  etiquetaInicio.addEventListener('input', () => { numeroEtiquetaAutomatico = false; });
  etiquetaInicio.addEventListener('change', () => {
    // Mostra o número já com zeros à esquerda assim que o fiscal sai do campo.
    if (/^\d+$/.test(etiquetaInicio.value.trim())) {
      etiquetaInicio.value = etiquetaInicio.value.trim().padStart(DIGITOS_ETIQUETA, '0');
      atualizarNumeroEtiqueta();
    }
  });

  const etiquetaOriginal = etiqueta.value.trim();
  if (etiquetaOriginal && !etiquetaInicio.value) etiquetaInicio.value = etiquetaOriginal;
  atualizarNumeroEtiqueta();

  // Sugere o próximo número livre ao trocar o tipo de etiqueta, enquanto o fiscal não digitar um número manualmente.
  let numeroEtiquetaAutomatico = !form.querySelector('input[name="registro_id"]');

  async function sugerirProximoNumeroEtiqueta(permissao) {
    if (!numeroEtiquetaAutomatico || (permissao !== 'permitido' && permissao !== 'todos')) return;
    try {
      const registroId = form.querySelector('input[name="registro_id"]')?.value || '';
      const parametros = new URLSearchParams({ permissao });
      if (registroId) parametros.set('excluir_id', registroId);
      const resposta = await fetch(`/api/teste-etiquetagem/proximo-numero-etiqueta?${parametros}`);
      if (!resposta.ok) return;
      const dados = await resposta.json();
      if (dados.numero && numeroEtiquetaAutomatico) {
        etiquetaInicio.value = dados.numero;
        atualizarNumeroEtiqueta();
      }
    } catch {
      // Falha silenciosa: o fiscal pode digitar o número manualmente.
    }
  }

  // Uma etiqueta "Não permitido" não tem número: a numeração só faz sentido para tipos permitidos.
  function atualizarVisibilidadeNumeroEtiqueta() {
    const naoPermitido = permissaoRadios.find((radio) => radio.checked)?.value === 'nao';
    if (grupoNumeroEtiqueta) grupoNumeroEtiqueta.hidden = naoPermitido;
    etiquetaInicio.required = !naoPermitido;
    etiqueta.required = !naoPermitido;
    if (naoPermitido) {
      etiquetaInicio.value = '';
      etiquetaFinal.value = '';
      etiqueta.value = '';
    }
  }

  permissaoRadios.forEach((radio) => {
    radio.addEventListener('change', () => {
      atualizarVisibilidadeNumeroEtiqueta();
      sugerirProximoNumeroEtiqueta(radio.value);
    });
  });
  atualizarVisibilidadeNumeroEtiqueta();

  adicionar.addEventListener('click', () => abrirPopupFrequencia());
  fecharPopupFrequencia.addEventListener('click', () => fecharPopupFrequenciaFn());
  popupFrequencia.addEventListener('click', (evento) => {
    if (evento.target === popupFrequencia) fecharPopupFrequenciaFn();
  });
  document.addEventListener('keydown', (evento) => {
    if (evento.key === 'Escape' && !popupFrequencia.hidden) fecharPopupFrequenciaFn();
  });

  const abrirNumerosEtiqueta = document.querySelector('#abrir-numeros-etiqueta');
  const popupNumerosEtiqueta = document.querySelector('#popup-numeros-etiqueta');
  const fecharNumerosEtiqueta = document.querySelector('#fechar-numeros-etiqueta');
  const numerosEtiquetaConteudo = document.querySelector('#numeros-etiqueta-conteudo');

  if (abrirNumerosEtiqueta && popupNumerosEtiqueta && fecharNumerosEtiqueta && numerosEtiquetaConteudo) {
    const escaparHtml = (texto) => String(texto ?? '').replace(/[&<>"']/g, (caractere) => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[caractere]
    ));
    const rotuloPermissao = (permissao) => (
      permissao === 'permitido' ? 'Permitido no local' : 'Permitido em todos'
    );
    const numeroFormatado = (numero) => String(numero).padStart(DIGITOS_ETIQUETA, '0');

    function tabelaFaixas(faixas) {
      if (!faixas.length) return '<p>Nenhuma faixa cadastrada para este evento.</p>';
      const linhas = faixas.map((item) => `<tr><td>${rotuloPermissao(item.permissao)}</td><td>${numeroFormatado(item.numero_inicial)}</td><td>${numeroFormatado(item.numero_final)}</td></tr>`).join('');
      return `<div class="table-scroll"><table class="ute-table"><thead><tr><th>Tipo</th><th>Início</th><th>Fim</th></tr></thead><tbody>${linhas}</tbody></table></div>`;
    }

    function tabelaOcupados(ocupados) {
      if (!ocupados.length) return '<p>Nenhum número ocupado até o momento.</p>';
      const linhas = ocupados.map((item) => `<tr><td>${rotuloPermissao(item.permissao)}</td><td>${numeroFormatado(item.numero_inicial)}</td><td>${numeroFormatado(item.numero_final)}</td><td>${escaparHtml(item.entidade)}</td><td>${escaparHtml(item.evento)}</td></tr>`).join('');
      return `<div class="table-scroll"><table class="ute-table"><thead><tr><th>Tipo</th><th>Início</th><th>Fim</th><th>Entidade</th><th>Evento</th></tr></thead><tbody>${linhas}</tbody></table></div>`;
    }

    async function carregarNumerosEtiqueta() {
      numerosEtiquetaConteudo.innerHTML = '<p class="form-help">Carregando...</p>';
      try {
        const resposta = await fetch('/api/teste-etiquetagem/numeros-etiqueta');
        if (!resposta.ok) throw new Error('Falha na consulta.');
        const dados = await resposta.json();
        numerosEtiquetaConteudo.innerHTML = `
          <h3 class="teq-title">Faixas cadastradas</h3>
          ${tabelaFaixas(dados.faixas || [])}
          <h3 class="teq-title">Números já ocupados</h3>
          ${tabelaOcupados(dados.ocupados || [])}
        `;
      } catch {
        numerosEtiquetaConteudo.innerHTML = '<p class="form-help">Não foi possível consultar os números agora.</p>';
      }
    }

    abrirNumerosEtiqueta.addEventListener('click', () => {
      popupNumerosEtiqueta.hidden = false;
      carregarNumerosEtiqueta();
    });
    fecharNumerosEtiqueta.addEventListener('click', () => { popupNumerosEtiqueta.hidden = true; });
    popupNumerosEtiqueta.addEventListener('click', (evento) => {
      if (evento.target === popupNumerosEtiqueta) popupNumerosEtiqueta.hidden = true;
    });
    document.addEventListener('keydown', (evento) => {
      if (evento.key === 'Escape' && !popupNumerosEtiqueta.hidden) popupNumerosEtiqueta.hidden = true;
    });
  }

  confirmarAdicionar.addEventListener('click', async () => {
    const valor = formatarFrequencia(frequencia.value);
    if (!valor) {
      frequencia.setCustomValidity('Informe uma frequência válida.');
      frequencia.reportValidity();
      frequencia.setCustomValidity('');
      return;
    }

    if (!passo.value.trim()) {
      passo.setCustomValidity('Selecione a Banda.');
      passo.reportValidity();
      passo.setCustomValidity('');
      return;
    }

    if (!faixa.value.trim()) {
      faixa.setCustomValidity('Selecione a Faixa.');
      faixa.reportValidity();
      faixa.setCustomValidity('');
      return;
    }

    const consulta = await consultarFrequencia(valor);

    if (frequenciaJaNaLista(valor)) {
      exibirConsulta(
        consulta || { equipamentos: [], referencias: [] },
        `A frequência ${valor} MHz já está na lista. A banda não altera o conflito.`
      );
      return;
    }

    const texto = `${valor} MHz ⌂ ${passo.value} • ${faixa.value}`;
    const existente = [...lista.options].some((opcao) => opcao.value === texto);
    if (existente) {
      [...lista.options].forEach((opcao) => { opcao.selected = false; });
      lista.querySelector(`option[value="${CSS.escape(texto)}"]`).selected = true;
      manterUmaSelecao();
      atualizarFrequenciasEnviadas();
      consultarFrequencia(valor);
      fecharPopupFrequenciaFn();
      return;
    }

    [...lista.options].forEach((opcao) => { opcao.selected = false; });
    const opcao = new Option(texto, texto, true, true);
    lista.add(opcao);
    manterUmaSelecao();
    atualizarFrequenciasEnviadas();
    limparErroSePreenchido('frequencias_selecionadas', lista.options.length > 0);
    fecharPopupFrequenciaFn();
  });

  remover.addEventListener('click', () => {
    if (remover.disabled || lista.selectedOptions.length === 0) return;
    [...lista.selectedOptions].forEach((opcao) => opcao.remove());
    atualizarEstadoRemover();
    atualizarFrequenciasEnviadas();
  });

  form.addEventListener('submit', () => {
    atualizarFrequenciasEnviadas();
  });

  manterUmaSelecao();
  atualizarFrequenciasEnviadas();
})();