const DB_NAME = 'appEventos';
const DB_VER  = 2;
const STORES  = ['pendencias', 'fila_envio', 'frequencias', 'fila_bsr_erb'];

// Abre (ou cria) o banco de dados
function abrirDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VER);
    req.onupgradeneeded = e => {
      const db = e.target.result;
      STORES.forEach(nome => {
        if (!db.objectStoreNames.contains(nome))
          db.createObjectStore(nome, { keyPath: 'id', autoIncrement: true });
      });
    };
    req.onsuccess = e => resolve(e.target.result);
    req.onerror   = e => reject(e.target.error);
  });
}

// Salva um array inteiro em uma store (substitui tudo)
async function salvarTodos(storeName, itens) {
  const db = await abrirDB();
  const tx = db.transaction(storeName, 'readwrite');
  tx.objectStore(storeName).clear();
  itens.forEach(item => tx.objectStore(storeName).add(item));
  return new Promise((res, rej) => {
    tx.oncomplete = () => res();
    tx.onerror    = e  => rej(e.target.error);
  });
}

// Lê todos os itens de uma store
async function lerTodos(storeName) {
  const db = await abrirDB();
  return new Promise((resolve, reject) => {
    const req = db.transaction(storeName, 'readonly')
                  .objectStore(storeName).getAll();
    req.onsuccess = e => resolve(e.target.result);
    req.onerror   = e => reject(e.target.error);
  });
}

// Adiciona um registro à fila de envio offline
async function enfileirar(storeName, payload) {
  const db = await abrirDB();
  return new Promise((resolve, reject) => {
    const req = db.transaction(storeName, 'readwrite')
                  .objectStore(storeName)
                  .add({ ...payload, timestamp: Date.now() });
    req.onsuccess = () => resolve();
    req.onerror   = e  => reject(e.target.error);
  });
}

// Remove da fila após envio bem-sucedido
async function removerDaFila(storeName, id) {
  const db = await abrirDB();
  db.transaction(storeName, 'readwrite')
    .objectStore(storeName).delete(id);
}
