(function () {
  const eventoSelect = document.querySelector('#evento_key');
  const fiscalSelect = document.querySelector('#fiscal_id');
  const papelSelect = document.querySelector('#papel');
  if (!eventoSelect || !fiscalSelect || !papelSelect) return;

  function resetFiscais(message) {
    fiscalSelect.replaceChildren();
    fiscalSelect.appendChild(new Option(message, ''));
    fiscalSelect.disabled = true;
    papelSelect.replaceChildren(new Option('Selecione um usuário primeiro', ''));
    papelSelect.disabled = true;
  }

  function popularFiscais(fiscais) {
    fiscalSelect.replaceChildren();
    fiscalSelect.appendChild(new Option('Selecione...', ''));
    fiscais.forEach((fiscal) => {
      const label = `${fiscal.nome} - ${fiscal.local_anatel}`;
      fiscalSelect.appendChild(new Option(label, String(fiscal.id)));
    });
    fiscalSelect.disabled = false;
  }

  fiscalSelect.addEventListener('change', () => {
    const fiscal = fiscaisAtuais.find((item) => String(item.id) === fiscalSelect.value);
    papelSelect.replaceChildren(new Option('Selecione...', ''));
    (fiscal?.papeis || []).forEach((papel) => papelSelect.appendChild(new Option(papel, papel)));
    papelSelect.disabled = !fiscal;
  });

  let fiscaisAtuais = [];

  eventoSelect.addEventListener('change', async () => {
    const eventoKey = eventoSelect.value;
    if (!eventoKey || !eventoKey.includes('|||')) {
      resetFiscais('Selecione um evento primeiro');
      return;
    }

    const eventoId = eventoKey.split('|||')[1];
    resetFiscais('Carregando usuários...');

    try {
      const response = await fetch(`/api/eventos/${encodeURIComponent(eventoId)}/fiscais`, {
        cache: 'no-store',
      });
      if (!response.ok) throw new Error('Falha ao carregar usuários');
      const fiscais = await response.json();

      if (!Array.isArray(fiscais) || fiscais.length === 0) {
        resetFiscais('Nenhum usuário vinculado ao evento');
        return;
      }

      fiscaisAtuais = fiscais;
      popularFiscais(fiscais);
    } catch {
      resetFiscais('Não foi possível carregar os usuários');
    }
  });
})();
