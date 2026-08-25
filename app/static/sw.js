const CACHE = "appEventos-v115";
const SHELL = [
  "/static/style.css",
  "/static/app.js",
  "/static/confirmacoes.js",
  "/static/db.js",
  "/static/sync.js",
  "/static/connectivity.js",
  "/static/header.js",
  "/static/sw-register.js",
  "/static/offline.html",
  "/static/consultar.js",
  "/static/inserir.js",
  "/static/bsr_erb.js",
  "/static/tabela_ute.js",
  "/static/selecao.js",
  "/static/teste_etiquetagem.js",
  "/static/upload-imagens.js",
];

// Instalação: pré-carrega os assets essenciais
self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(SHELL))
  );
  self.skipWaiting();
});

// Permite que a página force a ativação de um SW novo
self.addEventListener("message", e => {
  if (e.data && e.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
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

  // Só intercepta requests do próprio domínio. Requests externos (ex.: o ping
  // de conectividade ao gstatic) passam direto para a rede — assim eles
  // realmente falham quando está offline, sem cair no fallback do cache.
  if (url.origin !== self.location.origin) return;

  const ehEstatico = url.pathname.startsWith("/static/");

  // Assets estáticos: rede primeiro para evitar estilos/scripts obsoletos;
  // o cache permanece como fallback para o modo offline.
  if (ehEstatico) {
    e.respondWith(
      fetch(e.request, { cache: "no-store" })
        .then(res => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE).then(c => c.put(e.request, clone));
          }
          return res;
        })
        .catch(() =>
          caches.match(e.request).then(cached =>
            cached || caches.match(url.pathname)
          )
        )
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

