/**
 * app.js — Módulo offline centralizado do AppEventos
 * 
 * Gerencia IndexedDB, fila de envio, monitoramento de conectividade
 * e helpers para modo offline. Carregado em todas as telas via base.html.
 * 
 * Dependências: nenhuma (autocontido)
 * 
 * Uso:
 *   AppOffline.enfileirar('fila_envio', dados)
 *   AppOffline.sincronizarTudo()
 *   AppOffline.estaOffline()  // true/false
 */

const AppOffline = (() => {
  'use strict';

  const DB_NAME = 'appEventos';
  const DB_VER  = 3;
  const STORES  = ['fila_envio', 'fila_bsr_erb', 'cache_pendencias', 'cache_frequencias'];

  // ─── IndexedDB ───────────────────────────────────────────────

  async function _abrirDB() {
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

  // ─── API Pública ─────────────────────────────────────────────

  return {

    // --- Fila de envio offline ---

    /** Adiciona um item à fila para envio posterior */
    async enfileirar(storeName, payload) {
      const db = await _abrirDB();
      return new Promise((resolve, reject) => {
        const req = db.transaction(storeName, 'readwrite')
                      .objectStore(storeName)
                      .add({ ...payload, timestamp: Date.now() });
        req.onsuccess = () => resolve();
        req.onerror   = e => reject(e.target.error);
      });
    },

    /** Lê todos os itens de uma store */
    async lerTodos(storeName) {
      const db = await _abrirDB();
      return new Promise((resolve, reject) => {
        const req = db.transaction(storeName, 'readonly')
                      .objectStore(storeName).getAll();
        req.onsuccess = e => resolve(e.target.result);
        req.onerror   = e => reject(e.target.error);
      });
    },

    /** Remove um item da fila (após envio bem-sucedido) */
    async removerDaFila(storeName, id) {
      const db = await _abrirDB();
      db.transaction(storeName, 'readwrite')
        .objectStore(storeName).delete(id);
    },

    /** Salva um array inteiro em uma store (substitui tudo) */
    async salvarTodos(storeName, itens) {
      const db = await _abrirDB();
      const tx = db.transaction(storeName, 'readwrite');
      tx.objectStore(storeName).clear();
      itens.forEach(item => tx.objectStore(storeName).add(item));
      return new Promise((res, rej) => {
        tx.oncomplete = () => res();
        tx.onerror    = e => rej(e.target.error);
      });
    },

    // --- Sincronização ---

    /** Envia uma fila específica para o servidor */
    async sincronizarFila(storeName, url) {
      const fila = await this.lerTodos(storeName);
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
            await this.removerDaFila(storeName, item.id);
            console.log(`[sync] item ${item.id} enviado e removido de '${storeName}'.`);
          } else {
            console.warn(`[sync] servidor recusou item ${item.id}: ${resp.status}`);
          }
        } catch (e) {
          console.warn(`[sync] falha de rede ao enviar item ${item.id}:`, e);
        }
      }
    },

    /** Sincroniza todas as filas pendentes */
    async sincronizarTudo() {
      await this.sincronizarFila('fila_envio',  '/api/inserir');
      await this.sincronizarFila('fila_bsr_erb', '/api/bsr-erb');
    },

    // --- Conectividade ---

    /** Retorna true se estiver offline */
    estaOffline() {
      return !navigator.onLine;
    },

    // --- Helpers para formulários offline ---

    /**
     * Intercepta submit de formulário: tenta enviar via fetch.
     * Se falhar (rede), salva no IndexedDB para envio posterior.
     * 
     * @param {HTMLFormElement} form - O formulário
     * @param {string} url - URL para POST (ex: '/inserir')
     * @param {string} storeName - Nome da store (ex: 'fila_envio')
     * @param {Function} extrairDados - Função que extrai os dados do form para fila offline
     * @param {Object} opcoes - Opções adicionais
     */
    interceptarSubmit(form, url, storeName, extrairDados, opcoes = {}) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(form);

        // Tenta enviar para o servidor primeiro
        try {
          const resp = await fetch(url, {
            method: 'POST',
            body: fd,
          });
          if (resp.ok) {
            // Sucesso: servidor processou (pode ter redirecionado ou renderizado)
            if (resp.redirected) {
              window.location.href = resp.url;
            } else {
              // Se respondeu com HTML, substitui a página
              const html = await resp.text();
              document.open();
              document.write(html);
              document.close();
            }
            return;
          }
          // Se o servidor respondeu com erro, tenta salvar offline
          const text = await resp.text();
          // Se veio HTML com offline_salvo, o servidor já tratou
          if (text.includes('offline_salvo')) {
            document.open();
            document.write(text);
            document.close();
            return;
          }
        } catch (e) {
          // Falha de rede → continua para salvar offline
          console.warn('[offline] Falha na requisição, salvando localmente:', e);
        }

        // --- Modo offline: salva no IndexedDB ---
        const dados = extrairDados(fd);
        try {
          await this.enfileirar(storeName, dados);
          AppOfflineUI.mostrarSucesso(form, '📥 Salvo localmente. Será enviado ao reconectar.');
          form.reset();
        } catch (err) {
          AppOfflineUI.mostrarErro('Erro ao salvar localmente: ' + err);
        }
      });
    },
  };
})();


/**
 * AppOfflineUI — Componente de interface para modo offline
 * 
 * Gerencia banners, mensagens flash e feedback visual.
 * 
 * Uso:
 *   AppOfflineUI.iniciarMonitoramento()
 *   AppOfflineUI.mostrarSucesso(elemento, 'Mensagem')
 */
const AppOfflineUI = (() => {
  'use strict';

  return {

    /** Inicia monitoramento de conectividade com banner global */
    iniciarMonitoramento() {
      const banner = document.getElementById('offline-banner');
      if (!banner) return;

      function atualizar() {
        banner.classList.toggle('show', !navigator.onLine);
      }

      window.addEventListener('online', atualizar);
      window.addEventListener('offline', atualizar);
      atualizar(); // estado inicial
    },

    /** Exibe mensagem flash de sucesso antes de um elemento */
    mostrarSucesso(refElement, mensagem) {
      const div = document.createElement('div');
      div.className = 'flash flash-success';
      div.textContent = mensagem;
      refElement.parentElement.insertBefore(div, refElement);
    },

    /** Exibe mensagem flash de erro no topo da página */
    mostrarErro(mensagem) {
      const div = document.createElement('div');
      div.className = 'flash flash-error';
      div.textContent = mensagem;
      const container = document.querySelector('.container');
      if (container) {
        container.insertBefore(div, container.firstChild);
      }
    },
  };
})();


// ─── Inicialização automática ──────────────────────────────────

// Inicia monitoramento assim que o DOM estiver pronto
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    AppOfflineUI.iniciarMonitoramento();
    if (navigator.onLine) AppOffline.sincronizarTudo();
  });
} else {
  AppOfflineUI.iniciarMonitoramento();
  if (navigator.onLine) AppOffline.sincronizarTudo();
}

// Sincroniza ao recuperar conexão
window.addEventListener('online', () => {
  AppOffline.sincronizarTudo();
});