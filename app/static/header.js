(() => {
  document.addEventListener('keydown', (event) => {
    const elemento = event.target;
    const digitando = elemento.matches('input, textarea, select, [contenteditable="true"]');
    if (event.altKey && event.key.toLowerCase() === 'x' && !digitando) {
      event.preventDefault();
      window.location.href = '/menu';
    }
  });

  const form = document.querySelector('#evento-form');
  const select = document.querySelector('#evento-combo');
  if (!form || !select) return;

  select.addEventListener('change', () => {
    if (select.value) form.requestSubmit();
  });

  fetch(`/api/eventos?_=${Date.now()}`, { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error('Falha ao carregar eventos');
      return response.json();
    })
    .then((eventos) => {
      const eventoAtual = select.dataset.eventoAtual;
      select.replaceChildren();
      eventos.forEach((evento) => {
        const option = document.createElement('option');
        option.value = evento.key;
        option.textContent = evento.nome;
        option.selected = evento.nome === eventoAtual;
        select.appendChild(option);
      });
      if (!eventos.length) {
        select.appendChild(new Option('Nenhum evento disponível', ''));
      }
    })
    .catch(() => {
    });
})();
