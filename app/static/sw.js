const CACHE = "appEventos-v5";
const SHELL = [
  "/static/style.css",
  "/static/app.js",
  "/static/db.js",
  "/static/sync.js",
  "/static/offline.html",
];

// Instalação: pré-carrega os assets essenciais
self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(SHELL))
  );
  self.skipWaiting();
});

// Ativação: remove caches de versões antigas
self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: estratégia diferente para páginas dinâmicas vs. assets estáticos
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  // Ignora requests de extensões do Chrome (chrome-extension://)
  if (e.request.url.startsWith("chrome-extension://")) return;

  const url = new URL(e.request.url);
  const ehEstatico = url.pathname.startsWith("/static/");

  // Assets estáticos (CSS/JS/imagens): cache-first, atualiza em segundo plano
  if (ehEstatico) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        if (cached) return cached;
        return fetch(e.request).then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
          return res;
        });
      })
    );
    return;
  }

  // Páginas dinâmicas (/consultar, /menu, etc.): SEMPRE rede primeiro.
  // Só usa cache/offline.html se a rede falhar (offline real).
  e.respondWith(
    fetch(e.request)
      .then(res => res)
      .catch(() =>
        caches.match(e.request).then(cached =>
          cached || caches.match("/static/offline.html")
        )
      )
  );
});

