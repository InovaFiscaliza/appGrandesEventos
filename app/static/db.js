/**
 * db.js — Compatibilidade retroativa (DEPRECATED)
 * 
 * As funções agora estão centralizadas em app.js (AppOffline).
 * Mantido apenas para não quebrar código legado.
 * 
 * ☞ Use AppOffline.* nos novos desenvolvimentos.
 */

async function abrirDB()           { return AppOffline._abrirDB(); }
async function salvarTodos(n, i)   { return AppOffline.salvarTodos(n, i); }
async function lerTodos(n)         { return AppOffline.lerTodos(n); }
async function enfileirar(n, p)    { return AppOffline.enfileirar(n, p); }
async function removerDaFila(n, i) { return AppOffline.removerDaFila(n, i); }
