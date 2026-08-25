(function () {
  const eventoSelect = document.querySelector('#evento_key');
  const fiscalSelect = document.querySelector('#fiscal_id');
  if (!eventoSelect || !fiscalSelect) return;

  function resetFiscais(message) {
    fiscalSelect.replaceChildren();
    fiscalSelect.appendChild(new Option(message, ''));
    fiscalSelect.disabled = true;
  }

  function popularFiscais(fiscais) {
    fiscalSelect.replaceChildren();
    fiscalSelect.appendChild(new Option('Selecione...', ''));
    fiscais.forEach((fiscal) => {
      const label = `${fiscal.nome} - ${fiscal.local_anatel} (${fiscal.funcao_evento})`;
      fiscalSelect.appendChild(new Option(label, String(fiscal.id)));
    });
    fiscalSelect.disabled = false;
  }

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

      popularFiscais(fiscais);
    } catch {
      resetFiscais('Não foi possível carregar os usuários');
    }
  });
})();
