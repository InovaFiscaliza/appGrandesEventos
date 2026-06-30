const CACHE = "appEventos-v3";
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

// Fetch: tenta a rede primeiro, cai para cache se offline
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  // Ignora requests de extensões do Chrome (chrome-extension://)
  if (e.request.url.startsWith("chrome-extension://")) return;

  e.respondWith(
    fetch(e.request)
      .then(res => {
        const clone = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
        return res;
      })
      .catch(() =>
        caches.match(e.request).then(cached =>
          cached || caches.match("/static/offline.html")
        )
      )
  );
});
