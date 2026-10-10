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
    const papeis = (fiscal?.papeis || []).filter((papel) => eventoSelect.value !== '__novo__' || papel === 'Coordenação');
    papeis.forEach((papel) => papelSelect.appendChild(new Option(papel, papel)));
    if (eventoSelect.value === '__novo__' && fiscal) papelSelect.value = 'Coordenação';
    papelSelect.disabled = !fiscal;
  });

  let fiscaisAtuais = [];

  eventoSelect.addEventListener('change', async () => {
    const eventoKey = eventoSelect.value;
    fiscaisAtuais = [];
    const descricao = document.querySelector('#usuarios-login-descricao');
    if (descricao) descricao.textContent = eventoKey === '__novo__'
      ? 'Lista exibida somente com coordenadores cadastrados.'
      : 'Lista exibida com os fiscais vinculados ao evento.';
    if (eventoKey === '__novo__') {
      fiscaisAtuais = JSON.parse(document.querySelector('#coordenadores-login').textContent);
      if (fiscaisAtuais.length === 0) {
        resetFiscais('Nenhum coordenador cadastrado');
        return;
      }
      resetFiscais('Selecione um coordenador');
      popularFiscais(fiscaisAtuais);
      return;
    }
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
      if (eventoSelect.value !== eventoKey) return;

      if (!Array.isArray(fiscais) || fiscais.length === 0) {
        resetFiscais('Nenhum usuário vinculado ao evento');
        return;
      }

      fiscaisAtuais = fiscais;
      popularFiscais(fiscais);
    } catch {
      if (eventoSelect.value !== eventoKey) return;
      resetFiscais('Não foi possível carregar os usuários');
    }
  });
})();
