// Service worker Bible Quiz — permet de jouer hors-ligne après une première visite.
// Incrémenter CACHE_VERSION à chaque changement de index.html/CSS/JS pour forcer la mise à jour.
const CACHE_VERSION = 'bible-quiz-v2';
const APP_SHELL = ['/', '/index.html', '/manifest.json', '/icon-192.png', '/icon-512.png'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Les questions/catégories : réseau d'abord, mais on garde une copie pour jouer hors-ligne
  // (les parties précédemment jouées restent accessibles sans connexion).
  // Clé de cache normalisée par catégorie : on ignore player/exclude/limit,
  // sinon la moindre variation de ces paramètres fait manquer le cache hors-ligne.
  if (request.method === 'GET' && url.pathname === '/api/questions') {
    const category = url.searchParams.get('category') || 'MIX';
    const cacheKey = new Request(`/api/questions?category=${category}`);
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(cacheKey, clone));
          return response;
        })
        .catch(() => caches.match(cacheKey))
    );
    return;
  }

  if (request.method === 'GET' && url.pathname === '/api/categories') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(request, clone));
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Scores/réponses : toujours en ligne, jamais mis en cache (POST non cachable de toute façon).
  if (url.pathname.startsWith('/api/scores') || url.pathname.startsWith('/api/answer')) {
    return; // laisse passer normalement, échoue silencieusement hors-ligne (géré côté client)
  }

  // App shell et assets statiques : cache d'abord, puis réseau en secours.
  if (request.method === 'GET') {
    event.respondWith(
      caches.match(request).then((cached) => cached || fetch(request).catch(() => caches.match('/index.html')))
    );
  }
});
