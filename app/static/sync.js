// Requer db.js carregado antes deste script

async function sincronizarFila() {
  const fila = await lerTodos('fila_envio');
  if (fila.length === 0) return;

  console.log(`Sincronizando ${fila.length} item(ns) da fila...`);

  for (const item of fila) {
    try {
      const resp = await fetch(item.url, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(item.dados),
      });
      if (resp.ok) {
        await removerDaFila(item.id);
        console.log(`Item ${item.id} enviado e removido da fila.`);
      }
    } catch (e) {
      console.warn(`Falha ao enviar item ${item.id}:`, e);
    }
  }
}

// Executa ao recuperar conexão
window.addEventListener('online', sincronizarFila);
// Executa ao carregar a página (caso já esteja online)
if (navigator.onLine) sincronizarFila();
