(() => {
  const imagensExcluir = document.querySelector('#imagens-teste-excluir');
  document.querySelectorAll('.imagem-preview-excluir[data-imagem-id]').forEach((botao) => {
    botao.addEventListener('click', () => {
      const campo = document.createElement('input');
      campo.type = 'hidden';
      campo.name = 'imagens_excluir';
      campo.value = botao.dataset.imagemId;
      imagensExcluir?.appendChild(campo);
      botao.closest('.imagem-preview-item')?.remove();
    });
  });

  const frequencia = document.querySelector('#frequencia');
  const passo = document.querySelector('#passo');
  const faixa = document.querySelector('#faixa');
  const lista = document.querySelector('#frequencias');
  const frequenciasEnviadas = document.querySelector('#frequencias-enviadas');
  const frequenciaConsulta = document.querySelector('#frequencia-consulta');
  const cpfCnpj = document.querySelector('#cpfcnpj');
  const cpfCnpjAjuda = document.querySelector('#cpfcnpj-ajuda');
  const perfis = [...document.querySelectorAll('input[name="perfil"]')];
  const form = document.querySelector('.teq-form');
  const adicionar = document.querySelector('#adicionar-frequencia');
  const remover = document.querySelector('#remover-frequencia');

  if (!frequencia || !passo || !faixa || !lista || !frequenciasEnviadas || !frequenciaConsulta || !cpfCnpj || !cpfCnpjAjuda || !form || !adicionar || !remover) return;

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
        numero_etiqueta: document.querySelector('#numero-etiqueta'),
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
      const parametros = new URLSearchParams({ frequencia: String(numero) });
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
      cpfCnpjAjuda.classList.remove('teq-valid', 'teq-invalid');
      cpfCnpjAjuda.textContent = 'CPF/CNPJ não se aplica a estrangeiro.';
    } else {
      cpfCnpjAjuda.textContent = 'Informe um CPF ou CNPJ válido, se necessário.';
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
  document.querySelector('#numero-etiqueta')?.addEventListener('input', (event) => {
    limparErroSePreenchido('numero_etiqueta', event.target.value.trim().length > 0);
  });

  adicionar.addEventListener('click', async () => {
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
    if (consulta && (consulta.equipamentos.length > 0 || consulta.referencias.length > 0)) {
      return;
    }

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
      consultarFrequencia(valor);
      return;
    }

    [...lista.options].forEach((opcao) => { opcao.selected = false; });
    const opcao = new Option(texto, texto, true, true);
    lista.add(opcao);
    manterUmaSelecao();
    atualizarFrequenciasEnviadas();
    limparErroSePreenchido('frequencias_selecionadas', lista.options.length > 0);
    frequencia.value = '';
    frequencia.focus();
  });

  remover.addEventListener('click', () => {
    if (remover.disabled || lista.selectedOptions.length === 0) return;
    [...lista.selectedOptions].forEach((opcao) => opcao.remove());
    atualizarEstadoRemover();
    atualizarFrequenciasEnviadas();
  });

  manterUmaSelecao();
  atualizarFrequenciasEnviadas();
})();