(() => {
  const frequencia = document.querySelector('#frequencia');
  const passo = document.querySelector('#passo');
  const faixa = document.querySelector('#faixa');
  const lista = document.querySelector('#frequencias');
  const cpfCnpj = document.querySelector('#cpfcnpj');
  const cpfCnpjAjuda = document.querySelector('#cpfcnpj-ajuda');
  const form = document.querySelector('.teq-form');
  const adicionar = document.querySelector('#adicionar-frequencia');
  const remover = document.querySelector('#remover-frequencia');

  if (!frequencia || !passo || !faixa || !lista || !cpfCnpj || !cpfCnpjAjuda || !form || !adicionar || !remover) return;

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
    const numero = Number(valor.trim().replace(',', '.'));
    if (!Number.isFinite(numero) || numero <= 0) return null;
    return numero.toFixed(3).replace('.', ',');
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

  cpfCnpj.addEventListener('input', atualizarValidacaoCpfCnpj);
  atualizarValidacaoCpfCnpj();

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
  passo.addEventListener('change', () => {
    limparErroSePreenchido('passo', passo.value.trim().length > 0);
  });
  faixa.addEventListener('change', () => {
    limparErroSePreenchido('faixa', faixa.value.trim().length > 0);
  });
  lista.addEventListener('change', () => {
    limparErroSePreenchido('frequencias_selecionadas', lista.options.length > 0);
  });
  document.querySelector('#tipo-equipamento')?.addEventListener('change', (event) => {
    limparErroSePreenchido('tipo_equipamento', event.target.value.trim().length > 0);
  });
  document.querySelector('#numero-etiqueta')?.addEventListener('input', (event) => {
    limparErroSePreenchido('numero_etiqueta', event.target.value.trim().length > 0);
  });

  adicionar.addEventListener('click', () => {
    const valor = formatarFrequencia(frequencia.value);
    if (!valor) {
      frequencia.setCustomValidity('Informe uma frequência válida.');
      frequencia.reportValidity();
      frequencia.setCustomValidity('');
      return;
    }

    const texto = `${valor} ${passo.value} ${faixa.value}`;
    const existente = [...lista.options].some((opcao) => opcao.value === texto);
    if (existente) {
      lista.querySelector(`option[value="${CSS.escape(texto)}"]`).selected = true;
      return;
    }

    const opcao = new Option(texto, texto, true, true);
    lista.add(opcao);
    limparErroSePreenchido('frequencias_selecionadas', lista.options.length > 0);
    frequencia.value = '';
    frequencia.focus();
  });

  remover.addEventListener('click', () => {
    [...lista.selectedOptions].forEach((opcao) => opcao.remove());
  });
})();