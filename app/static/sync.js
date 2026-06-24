// Requer db.js carregado antes deste script

async function sincronizarFila(storeName, url) {
  const fila = await lerTodos(storeName);
  if (fila.length === 0) return;

  console.log(`[sync] ${storeName}: ${fila.length} item(ns) pendente(s)...`);

  for (const item of fila) {
    try {
      const { id, timestamp, ...dados } = item;
      const resp = await fetch(url, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(dados),
      });
      if (resp.ok) {
        await removerDaFila(storeName, item.id);
        console.log(`[sync] item ${item.id} enviado e removido de '${storeName}'.`);
      } else {
        console.warn(`[sync] servidor recusou item ${item.id}: ${resp.status}`);
      }
    } catch (e) {
      console.warn(`[sync] falha de rede ao enviar item ${item.id}:`, e);
    }
  }
}

async function sincronizarTudo() {
  await sincronizarFila('fila_envio',  '/api/inserir');
  await sincronizarFila('fila_bsr_erb', '/api/bsr-erb');
}

// Executa ao recuperar conexão
window.addEventListener('online', sincronizarTudo);
// Executa ao carregar a página (caso já esteja online)
if (navigator.onLine) sincronizarTudo();
