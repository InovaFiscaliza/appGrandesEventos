(() => {
  const frequencia = document.querySelector('#frequencia');
  const passo = document.querySelector('#passo');
  const faixa = document.querySelector('#faixa');
  const lista = document.querySelector('#frequencias');
  const adicionar = document.querySelector('#adicionar-frequencia');
  const remover = document.querySelector('#remover-frequencia');

  if (!frequencia || !passo || !faixa || !lista || !adicionar || !remover) return;

  function formatarFrequencia(valor) {
    const numero = Number(valor.trim().replace(',', '.'));
    if (!Number.isFinite(numero) || numero <= 0) return null;
    return numero.toFixed(3).replace('.', ',');
  }

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
    frequencia.value = '';
    frequencia.focus();
  });

  remover.addEventListener('click', () => {
    [...lista.selectedOptions].forEach((opcao) => opcao.remove());
  });
})();